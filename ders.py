import streamlit as st
import PyPDF2
from transformers import pipeline

# --- 1. Başlık ---
st.title("📄 PDF Özetleme ve Soru-Cevap Uygulaması")

# --- 2. PDF yükleme ---
uploaded_file = st.file_uploader("Bir PDF dosyası yükleyin", type=["pdf"])

if uploaded_file:
    # --- 3. Sayfa sayısını öğren ---
    reader = PyPDF2.PdfReader(uploaded_file)
    total_pages = len(reader.pages)
    st.info(f"PDF toplam {total_pages} sayfa içeriyor.")

    # --- 4. Sayfa aralığı seçimi ---
    start_page = st.number_input("Başlangıç sayfası", min_value=1, max_value=total_pages, value=1)
    end_page = st.number_input("Bitiş sayfası", min_value=1, max_value=total_pages, value=total_pages)

    if st.button("📚 Sayfaları Oku ve Özetle"):
        text = ""
        for i in range(start_page-1, end_page):
            text += reader.pages[i].extract_text()

        st.subheader("📝 Seçilen Sayfa Metni")
        st.text_area("PDF içeriği:", text[:2000] + "..." if len(text) > 2000 else text, height=200)

        # --- 5. Özetleme ---
        st.subheader("🔍 Özet oluşturuluyor...")
        summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        summary = summarizer(text, max_length=300, min_length=60, do_sample=False)[0]["summary_text"]

        st.success("✅ Özet:")
        st.write(summary)

        # --- 6. Soru-Cevap ---
        st.subheader("❓ Soru Sor")
        qa_pipeline = pipeline("question-answering", model="deepset/roberta-base-squad2")

        question = st.text_input("Sorunuzu yazın (örnek: Bu bölüm ne hakkında?)")

        if question:
            answer = qa_pipeline(question=question, context=text)
            st.markdown(f"**Cevap:** {answer['answer']}")

