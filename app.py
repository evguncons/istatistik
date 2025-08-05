import streamlit as st
import streamlit.components.v1 as components
import os

# -----------------------------------------------------------------------------
# Sayfa Konfigürasyonu
# -----------------------------------------------------------------------------
# Streamlit sayfasının temel ayarları. Sayfa başlığı, ikonu ve yerleşim düzeni belirlenir.
st.set_page_config(
    page_title="Hedef AVM Online Satış İstatistik",
    page_icon="🏆",
    layout="wide"  # HTML içeriğinin tam genişlikte görüntülenmesini sağlar.
)

# -----------------------------------------------------------------------------
# Tam Ekran, Çerçevesiz ve Mobil Uyumlu Bileşen için Özel CSS
# -----------------------------------------------------------------------------
# Bu CSS kodu, Streamlit'in varsayılan kenar boşluklarını kaldırır ve iframe'in
# tüm ekranı kaplamasını sağlayarak mobil kaydırma sorunlarını çözer.
st.markdown("""
    <style>
        /* Ana sayfanın kaydırma çubuğunu gizle */
        body {
            overflow: hidden; 
        }
        
        /* Streamlit tarafından eklenen tüm kenar boşluklarını kaldır */
        .block-container {
            padding: 0 !important;
            margin: 0 !important;
        }

        /* Bileşenin bulunduğu iframe'in tüm ekranı kaplamasını sağla */
        iframe {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            border: none;
        }
    </style>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# HTML Dosyasını Okuma ve Gösterme
# -----------------------------------------------------------------------------
# Bu bölüm, `app.py` ile aynı dizinde bulunan 'index.html' dosyasını bulur,
# içeriğini okur ve Streamlit'in `components.html` özelliğini kullanarak
# ekranda görüntüler.

# HTML dosyasının yolu (app.py ile aynı dizinde olduğu varsayılır)
html_file_path = os.path.join(os.path.dirname(__file__), 'index.html')

try:
    # HTML dosyasını UTF-8 kodlamasıyla oku
    with open(html_file_path, 'r', encoding='utf-8') as f:
        html_code = f.read()

    # HTML içeriğini Streamlit bileşeni olarak göster.
    # `height` parametresi kaldırıldı, çünkü boyutlandırma artık CSS ile kontrol ediliyor.
    # `scrolling=True`, HTML içeriğinin kendi içinde kaydırılmasına izin verir.
    components.html(html_code, scrolling=True)

except FileNotFoundError:
    # `index.html` dosyası bulunamazsa kullanıcıya bilgilendirici bir hata mesajı gösterilir.
    st.error(f"HATA: '{html_file_path}' konumunda `index.html` dosyası bulunamadı.")
    st.warning(
        "Lütfen aşağıdaki adımları kontrol edin:\n"
        "1. Canvas'taki HTML kodunun tamamını kopyalayıp `index.html` adıyla kaydettiğinizden emin olun.\n"
        "2. `index.html` dosyasının `app.py` dosyasıyla aynı klasörde olduğundan emin olun."
    )
except Exception as e:
    st.error(f"HTML dosyası okunurken beklenmedik bir hata oluştu: {e}")

