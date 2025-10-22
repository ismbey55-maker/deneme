import streamlit as st
import PyPDF2
import requests
from io import BytesIO
from transformers import pipeline

# --- Başlık ---
st.title("📘 PDF Özetleme ve Soru-Cevap Uygulaması")

# --- GitHub PDF URL'si girişi ---
pdf_url = st.text_input("📎 GitHub PDF dosya URL'si girin (örnek: https://github.com/.../edebiyat.pdf):")

# --- Sayfa aralığı seçimi ---
page_range = st.text_input("📄 Özetlenecek sayfa aralığı (örnek: 2-5):")

# --- Model yükleme ---
@st.cache_resource
def load_models():
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    qa_model = pipeline("question-answering", model="deepset/roberta-base-squad2")
    return summarizer, qa_model

summarizer, qa_model = load_models()

# --- PDF okuma fonksiyonu ---
def read_pdf_from_url(url, start_page, end_page):
    response = requests.get(url)
    pdf_file = BytesIO(response.content)
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for i in range(start_page - 1, end_page):
        if i < len(reader.pages):
            text += reader.pages[i].extract_text() + "\n"
    return text

# --- İşlem başlat ---
if st.button("📖 PDF'yi Oku ve Özetle"):
    if pdf_url and page_range:
        try:
            start, end = map(int, page_range.split('-'))
            pdf_text = read_pdf_from_url(pdf_url, start, end)

            with st.spinner("Özet çıkarılıyor..."):
                summary = summarizer(pdf_text, max_length=250, min_length=50, do_sample=False)[0]['summary_text']
            
            st.subheader("📜 Özet:")
            st.write(summary)

            with st.spinner("Soru-Cevap üretiliyor..."):
                example_questions = [
                    "Bu bölümün ana fikri nedir?",
                    "Metinde hangi konu ele alınmıştır?",
                    "Önemli detaylar nelerdir?"
                ]
                for q in example_questions:
                    ans = qa_model(question=q, context=summary)
                    st.markdown(f"**❓ {q}**")
                    st.write(f"💬 {ans['answer']}")
            
            # Kullanıcı kendi sorusunu sorsun
            st.subheader("🔎 Kendi Sorunu Sor:")
            user_q = st.text_input("Sorunuzu yazın:")
            if st.button("Cevapla"):
                if user_q.strip():
                    ans = qa_model(question=user_q, context=summary)
                    st.markdown(f"**❓ {user_q}**")
                    st.write(f"💬 {ans['answer']}")
        except Exception as e:
            st.error(f"Hata: {e}")
    else:
        st.warning("Lütfen PDF URL'si ve sayfa aralığını girin.")

# --- Çıkış butonu ---
if st.button("🚪 Çıkış"):
    st.success("Uygulama kapatılıyor...")
    st.stop()
