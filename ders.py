import streamlit as st
import PyPDF2
from transformers import pipeline

st.title("PDF Sayfa Okuma ve Özet Çıkarma (Türkçe)")

# PDF yükleme
pdf_file = st.file_uploader("PDF dosyasını yükleyin", type="pdf")

if pdf_file is not None:
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    total_pages = len(pdf_reader.pages)
    st.write(f"PDF sayfa sayısı: {total_pages}")

    # Sayfa aralığı seçimi
    start_page = st.number_input("Başlangıç sayfası", min_value=1, max_value=total_pages, value=1)
    end_page = st.number_input("Bitiş sayfası", min_value=1, max_value=total_pages, value=total_pages)

    if st.button("Özetle"):
        if start_page > end_page:
            st.error("Başlangıç sayfası bitiş sayfasından büyük olamaz!")
        else:
            # Seçilen sayfaları oku
            text = ""
            for i in range(start_page-1, end_page):
                page = pdf_reader.pages[i]
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            
            if text.strip() == "":
                st.warning("PDF’den metin çıkarılamadı.")
            else:
                # Hugging Face özetleme pipeline
                summarizer = pipeline("summarization", model="t5-base")  # Türkçe için t5-base, dil Türkçe değilse mBART/mt5 önerilir
                # Uzun metinleri parçala
                max_chunk = 1000
                chunks = [text[i:i+max_chunk] for i in range(0, len(text), max_chunk)]
                summary_text = ""
                for chunk in chunks:
                    summary = summarizer(chunk, max_length=150, min_length=50, do_sample=False)
                    summary_text += summary[0]['summary_text'] + "\n"

                st.subheader("Özet")
                st.write(summary_text)
