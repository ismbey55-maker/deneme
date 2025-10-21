import streamlit as st
import PyPDF2
from transformers import pipeline

# Başlık
st.title("📄 PDF Türkçe Özet ve Otomatik Soru-Cevap")

# PDF dosyasını yükle
uploaded_file = st.file_uploader("Bir PDF dosyası yükleyin", type=["pdf"])

if uploaded_file:
    reader = PyPDF2.PdfReader(uploaded_file)
    total_pages = len(reader.pages)
    st.info(f"PDF toplam {total_pages} sayfa içeriyor.")

    start_page = st.number_input("Başlangıç sayfası", min_value=1, max_value=total_pages, value=1)
    end_page = st.number_input("Bitiş sayfası", min_value=1, max_value=total_pages, value=total_pages)

    if st.button("📚 Sayfaları Oku ve Özetle"):
        # PDF metnini al
        text = ""
        for i in range(start_page-1, end_page):
            text += reader.pages[i].extract_text()

        st.subheader("📝 PDF Metni")
        st.text_area("Metin:", text[:2000] + "..." if len(text) > 2000 else text, height=200)

        # Özetleme (Türkçe)
        st.subheader("🔍 Özet oluşturuluyor...")
        summarizer = pipeline("summarization", model="marmara/mt5-small-turkish-summarization")

        max_chunk = 1000
        text_chunks = [text[i:i+max_chunk] for i in range(0, len(text), max_chunk)]

        summary = ""
        for chunk in text_chunks:
            summary += summarizer(chunk, max_length=150, min_length=30, do_sample=False)[0]["summary_text"] + " "

        st.success("✅ Özet (Türkçe):")
        st.write(summary)

        # Otomatik Soru-Cevap
        st.subheader("❓ Otomatik Soru-Cevap")
        qa_pipeline = pipeline("question-generation")  # HuggingFace question-generation pipeline
        qg_model = pipeline("question-answering", model="deepset/roberta-base-squad2")  # cevap için

        if st.button("🌀 Yeni Soru-Cevap Üret"):
            # Özet üzerinden soru üret
            question = "Bu metin ne hakkında?"  # Özet üzerinden genel soru
            answer = qg_model(question=question, context=summary)
            st.markdown(f"**Soru:** {question}")
            st.markdown(f"**Cevap:** {answer['answer']}")
