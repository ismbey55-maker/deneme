import streamlit as st
import pandas as pd
import random
import os

# Belirtilen dosya yolu
# LÜTFEN BU YOLU KENDİ DOSYA FORMATINIZA GÖRE GÜNCELLEYİNİZ (örneğin: /home/mrt/ahmet/kelime.xlsx)
#DOSYA_YOLU = "/home/mrt/ahmet/kelime.csv" 
DOSYA_YOLU = "kelime.csv" 

def dosyayi_oku(dosya_yolu):
    """Verilen yoldaki CSV veya XLSX dosyasını okur ve DataFrame döndürür."""
    if not os.path.exists(dosya_yolu):
        st.error(f"HATA: Dosya bulunamadı: {dosya_yolu}")
        st.info("Lütfen dosyayı kontrol edin ve **CSV (.csv)** veya **Excel (.xlsx)** formatında kaydettiğinizden emin olun.")
        return None
        
    try:
        if dosya_yolu.endswith('.csv'):
            # Türkçe karakterler için farklı encoding denemeleri
            try:
                df = pd.read_csv(dosya_yolu, header=0, encoding='utf-8')
            except UnicodeDecodeError:
                df = pd.read_csv(dosya_yolu, header=0, encoding='latin-1')
        elif dosya_yolu.endswith('.xlsx'):
            df = pd.read_excel(dosya_yolu, header=0)
        else:
            st.error("Desteklenmeyen dosya formatı. Lütfen CSV (.csv) veya Excel (.xlsx) kullanın.")
            return None
        
        # Sütun isimlerini standartlaştır (İlk sütun İngilizce, ikinci Türkçe varsayılır)
        df.columns = ['Ingilizce', 'Turkce']
        return df

    except Exception as e:
        st.error(f"HATA: Dosya okunurken bir sorun oluştu. Hata: {e}")
        st.info("Dosyanızın ilk satırının başlık (İngilizce, Türkçe) içerdiğinden emin olun.")
        return None

def state_i_baslat():
    """Streamlit oturum durumunu (session state) başlatır veya sıfırlar."""
    df = dosyayi_oku(DOSYA_YOLU)
    
    if df is None or df.empty:
        return

    kelime_sozlugu = df.set_index('Ingilizce')['Turkce'].to_dict()
    ingilizce_kelimeler = list(kelime_sozlugu.keys())
    
    if not ingilizce_kelimeler:
        st.error("Dosyada kelime bulunamadı. Lütfen dosya içeriğini kontrol edin.")
        return

    # Tüm başlangıç değerlerini ayarla
    st.session_state['kelime_sozlugu'] = kelime_sozlugu
    st.session_state['karisik_kelimeler'] = random.sample(ingilizce_kelimeler, len(ingilizce_kelimeler))
    st.session_state['mevcut_index'] = 0
    st.session_state['skor'] = 0
    st.session_state['denemeler'] = 0
    st.session_state['oyun_aktif'] = True
    st.session_state['mesaj'] = ""
    st.session_state['cevap_gosterildi'] = False # Kontrol sonrası durumu
    if 'tahmin_input' in st.session_state:
        del st.session_state['tahmin_input'] # Inputu temizle

def sonraki_kelimeye_ilerle():
    """Bir sonraki kelimeye geçer veya oyunu bitirir."""
    st.session_state.mevcut_index += 1
    st.session_state.cevap_gosterildi = False
    st.session_state.mesaj = ""
    
    # Input değerini temizle
    if 'tahmin_input' in st.session_state:
        st.session_state['tahmin_input'] = ""

    if st.session_state.mevcut_index >= len(st.session_state.karisik_kelimeler):
        st.session_state.oyun_aktif = False
        st.session_state.mesaj = f"OYUN BİTTİ! Toplam Skorunuz: {st.session_state.skor} / {len(st.session_state.karisik_kelimeler)}"

def cevap_kontrol():
    """Kullanıcının tahminini kontrol eder ve sonucu gösterir."""
    if not st.session_state.oyun_aktif:
        return
    if st.session_state.cevap_gosterildi: # Zaten kontrol edilmişse tekrar çalıştırma
        return

    # st.session_state.tahmin_input, text_input'tan gelen son değeri tutar
    tahmin = st.session_state.tahmin_input.strip()
    mevcut_kelime = st.session_state.karisik_kelimeler[st.session_state.mevcut_index]
    dogru_cevap = st.session_state.kelime_sozlugu[mevcut_kelime]
    
    st.session_state.denemeler += 1

    if tahmin.lower() == dogru_cevap.lower():
        st.session_state.skor += 1
        st.session_state.mesaj = f"✅ Tebrikler! Doğru cevap: **{dogru_cevap}**"
    else:
        st.session_state.mesaj = f"❌ Maalesef yanlış. Doğru cevap: **{dogru_cevap}**"
    
    st.session_state.cevap_gosterildi = True # Cevabın gösterildiğini işaretle
    # Streamlit, bu fonksiyondan sonra otomatik olarak yeniden çalışır.


# --- Streamlit Uygulama Düzeni ---

st.set_page_config(
    page_title="A1 İngilizce Kelime Ezberleme",
    layout="centered"
)

st.title("📚 A1 - İngilizce Kelime Ezberleme ")
#st.caption(f"Kelimeler: `{DOSYA_YOLU}` dosyasından yüklenmiştir.")

# Oyun durumunu kontrol et ve başlat
if 'oyun_aktif' not in st.session_state or ('oyun_aktif' in st.session_state and not st.session_state.oyun_aktif and st.session_state.mesaj == ""):
     state_i_baslat()


if 'oyun_aktif' in st.session_state and st.session_state.oyun_aktif:
    
    mevcut_kelime = st.session_state.karisik_kelimeler[st.session_state.mevcut_index]
    toplam_kelime = len(st.session_state.karisik_kelimeler)

    # Skor ve kelime bilgileri
    st.markdown(f"**Kelime: {st.session_state.mevcut_index + 1} / {toplam_kelime}**")
    st.markdown(f"**Doğru Skor: {st.session_state.skor} / {st.session_state.mevcut_index}**")
    st.markdown("---")

    # Sorulan Kelime
    st.subheader(f"❓ {mevcut_kelime.upper()} ❓")
    st.markdown("---")

    # Tahmin girişi ve butonlar
    tahmin_col, kontrol_col, sonraki_col = st.columns([2, 1, 1])
    
    with tahmin_col:
        st.text_input(
            "Türkçe anlamını girin:",
            key="tahmin_input",
            disabled=st.session_state.cevap_gosterildi, # Cevap gösterildiyse inputu kilitle
            on_change=cevap_kontrol if not st.session_state.cevap_gosterildi else None, # Enter'a basınca kontrol et
            label_visibility="collapsed"
        )
    
    with kontrol_col:
        st.button(
            "Kontrol Et", 
            on_click=cevap_kontrol, 
            type="primary",
            disabled=st.session_state.cevap_gosterildi or not ('tahmin_input' in st.session_state and st.session_state.tahmin_input) # Cevap gösterildiyse veya input boşsa kilitli
        )
    
    with sonraki_col:
        # Cevap gösterildikten sonra bu buton görünür olur
        st.button(
            "Sonraki Kelime >>", 
            on_click=sonraki_kelimeye_ilerle, 
            disabled=not st.session_state.cevap_gosterildi, # Cevap gösterilmediyse kilitli
            type="secondary"
        )


    # Sonuç mesajı
    if st.session_state.mesaj:
        # Cevap mesajını göster
        st.markdown(f"#### {st.session_state.mesaj}")

# Oyun Bitti Durumu
elif 'oyun_aktif' in st.session_state and not st.session_state.oyun_aktif:
    st.success(f"🎉 Tebrikler! Oyunu Bitirdiniz! 🎉")
    st.subheader(f"Nihai Skorunuz: {st.session_state.skor} / {len(st.session_state.karisik_kelimeler)}")
    st.info(f"Toplam deneme sayınız: {st.session_state.denemeler}")
    st.button("Yeniden Başla", on_click=state_i_baslat)

# Hata Durumu
else:
    st.error("Uygulama başlatılamadı veya kelime dosyası yüklenemedi. Lütfen konsol çıktılarını ve dosya yolunu kontrol edin.")
    st.button("Tekrar Dene", on_click=state_i_baslat)