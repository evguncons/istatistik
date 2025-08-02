import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime

# -----------------------------------------------------------------------------
# Sayfa Yapılandırması ve Sabitler
# -----------------------------------------------------------------------------

st.set_page_config(
    page_title="HedefAVM Satış Paneli",
    page_icon="https://static.ticimax.cloud/32769/uploads/editoruploads/hedef-image/logo.png",
    layout="wide"
)

# Google Apps Script URL'niz
APPS_SCRIPT_URL = 'https://script.google.com/macros/s/AKfycbxSquBU2QkyB79SkPSPHPd7BKJfiJZB3su85LosK7YBcRe4vdrrAAczgp3LOuCC76Xp7A/exec'

# -----------------------------------------------------------------------------
# Özel CSS ile Arayüzü Güzelleştirme
# -----------------------------------------------------------------------------

def load_css():
    """index.html dosyasındaki temayı taklit eden özel CSS stillerini yükler."""
    st.markdown("""
        <style>
            /* Google Font'u Yükle */
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
            
            /* Genel arayüz ve fontlar */
            html, body, [class*="st-"] {
                font-family: 'Inter', sans-serif;
            }
            /* Streamlit'in ana arkaplanını ve padding'ini ayarla */
            .main .block-container {
                padding-top: 2rem;
                padding-bottom: 2rem;
                padding-left: 2rem;
                padding-right: 2rem;
            }
            .stApp {
                background-color: #f4f7fe;
            }
            /* Kart stilini taklit eden container */
            .card {
                background-color: #ffffff;
                border-radius: 20px;
                padding: 24px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
                height: 100%;
            }
            /* Metriklerin (sayısal göstergeler) stilini düzenleme */
            [data-testid="stMetricValue"] {
                font-size: 2.5rem !important;
                font-weight: 800 !important;
                color: #6D28D9 !important;
            }
            [data-testid="stMetricLabel"] {
                font-size: 1rem !important;
                font-weight: 600 !important;
                color: #4a5568 !important;
            }
            /* Başlık stilleri */
            h1 {
                font-weight: 800;
                color: #1a202c;
            }
            h2, h3 {
                color: #1a202c;
                font-weight: 700;
            }
            /* Buton stilini düzenleme */
            .stButton>button {
                border-radius: 12px !important;
                font-weight: 600 !important;
                background-color: #6D28D9 !important;
                color: white !important;
                width: 100%;
                padding: 12px 24px !important;
                border: none !important;
            }
            .stButton>button:hover {
                background-color: #5B21B6 !important;
                color: white !important;
            }
        </style>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Veri Çekme ve İşleme Fonksiyonları
# -----------------------------------------------------------------------------

@st.cache_data(ttl=600)  # Veriyi 10 dakika boyunca önbellekte tut
def fetch_data(action, params=None):
    """Google Apps Script'ten veri çeker."""
    if params is None:
        params = {}
    params['t'] = datetime.now().timestamp()
    
    try:
        response = requests.get(f"{APPS_SCRIPT_URL}?action={action}", params=params)
        response.raise_for_status()
        data = response.json()
        if data.get('error'):
            st.error(f"API Hatası: {data['error']}")
            return None
        return data
    except requests.exceptions.RequestException as e:
        st.error(f"Veri çekme hatası: {e}")
        return None

def format_currency(value):
    """Sayısal değeri Türkçe para formatına çevirir."""
    return f"{value:,.2f} ₺".replace(",", "X").replace(".", ",").replace("X", ".")

# -----------------------------------------------------------------------------
# Ana Arayüz Başlangıcı
# -----------------------------------------------------------------------------

load_css()

# --- Başlık ---
header_col1, header_col2 = st.columns([1, 10])
with header_col1:
    st.image("https://static.ticimax.cloud/32769/uploads/editoruploads/hedef-image/logo.png", width=70)
with header_col2:
    st.title("Hedef AVM Online Satış İstatistik")

# --- Filtreler ---
periods_data = fetch_data('getAvailablePeriods')
if periods_data and periods_data.get('periods'):
    month_order = ['OCAK', 'ŞUBAT', 'MART', 'NİSAN', 'MAYIS', 'HAZİRAN', 'TEMMUZ', 'AĞUSTOS', 'EYLÜL', 'EKİM', 'KASIM', 'ARALIK']
    
    def get_period_sort_key(period_string):
        try:
            parts = period_string.split(' ')
            if len(parts) == 2:
                month, year = parts[0].upper(), int(parts[1])
                if month in month_order:
                    return (year, month_order.index(month))
        except (ValueError, IndexError):
            pass
        return (0, 0)

    periods = sorted(periods_data['periods'], key=get_period_sort_key, reverse=True)
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    filter_col1, filter_col2, filter_col3 = st.columns([2,2,1])
    with filter_col1:
        st.subheader("Dönem Seçimi")
    with filter_col2:
        selected_period = st.selectbox("Dönem", periods, label_visibility="collapsed")
    with filter_col3:
        getir_button = st.button("Getir")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown(f"### **{selected_period}** Dönemi Analizi")
    
    # --- Veri Yükleme ve Gösterge Paneli ---
    if selected_period:
        data = fetch_data('getLeaderboard', {'sheetName': selected_period})
        
        if data and data.get('leaderboard'):
            df_leaderboard = pd.DataFrame(data['leaderboard'])
            df_raw_sales = pd.DataFrame(data['rawSales'])

            # Veri tiplerini güvenli bir şekilde dönüştür
            df_leaderboard['totalCiro'] = pd.to_numeric(df_leaderboard['totalCiro'], errors='coerce').fillna(0)
            df_leaderboard['successfulSalesCount'] = pd.to_numeric(df_leaderboard['successfulSalesCount'], errors='coerce').fillna(0)
            if 'tutar' in df_raw_sales.columns:
                df_raw_sales['tutar'] = pd.to_numeric(df_raw_sales['tutar'], errors='coerce').fillna(0)
            else:
                df_raw_sales['tutar'] = 0

            # --- Üst Metrikler ---
            total_ciro = df_leaderboard['totalCiro'].sum()
            total_sales_count = df_leaderboard['successfulSalesCount'].sum()
            avg_sale_amount = total_ciro / total_sales_count if total_sales_count > 0 else 0

            metric_col1, metric_col2 = st.columns(2)
            with metric_col1:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.metric(label="Dönem Toplam Ciro", value=format_currency(total_ciro))
                st.markdown('</div>', unsafe_allow_html=True)
            with metric_col2:
                 st.markdown('<div class="card" style="text-align: center;">', unsafe_allow_html=True)
                 st.subheader("Satış Performansı")
                 if st.button("Aylık Trendi Görüntüle", key="trend_button_main"):
                     st.session_state.show_trend = True
                 st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)

            # --- Şube ve Kategori Analizi ---
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("Şubeler Ciro Karşılaştırması")
            if not df_leaderboard.empty and df_leaderboard['totalCiro'].sum() > 0:
                df_sorted = df_leaderboard.sort_values("totalCiro", ascending=True)
                fig = px.bar(df_sorted, x="totalCiro", y="branch", orientation='h', text_auto='.2s', labels={"totalCiro": "Toplam Ciro (₺)", "branch": "Şube"})
                fig.update_traces(marker_color='#6D28D9', textposition='outside')
                fig.update_layout(yaxis_title=None, xaxis_title=None, showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Bu dönem için şube ciro verisi bulunamadı.")
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)

            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("Bu Ay En Çok Satılan Kategoriler")
            if not df_raw_sales.empty:
                df_sold = df_raw_sales[df_raw_sales['result'].str.lower() == 'satışa döndü']
                category_counts = df_sold['category'].value_counts().reset_index()
                category_counts.columns = ['Kategori', 'Satış Adedi']
                
                if not category_counts.empty:
                    for index, row in category_counts.iterrows():
                        category_name = row['Kategori']
                        sales_count = row['Satış Adedi']
                        with st.expander(f"{category_name} - {sales_count} Satış"):
                            df_category = df_sold[df_sold['category'] == category_name]
                            category_ciro = df_category['tutar'].sum()
                            st.markdown(f"**Toplam Ciro:** {format_currency(category_ciro)}")
                            if not df_category.empty:
                                top_branch = df_category['branch'].value_counts().idxmax()
                                st.markdown(f"**En Çok Satan Şube:** {top_branch}")
                else:
                    st.info("Bu dönem için satılan kategori bulunamadı.")
            else:
                st.info("Kategori verisi mevcut değil.")
            st.markdown('</div>', unsafe_allow_html=True)

            # --- Aylık Trend Grafiği (Modal/Dialog içinde) ---
            if 'show_trend' not in st.session_state:
                st.session_state.show_trend = False

            if st.session_state.show_trend:
                with st.dialog("Aylık Ciro Trendi"):
                    trend_data = fetch_data('getMonthlyTrendData')
                    if trend_data:
                        df_trend = pd.DataFrame(trend_data)
                        df_trend['totalCiro'] = pd.to_numeric(df_trend['totalCiro'], errors='coerce').fillna(0)
                        df_trend['sort_key'] = df_trend['period'].apply(get_period_sort_key)
                        df_trend = df_trend.sort_values('sort_key').reset_index(drop=True)
                        
                        st.subheader("Aylık Ciro Trendi")
                        fig_trend = px.line(df_trend, x='period', y='totalCiro', markers=True, labels={"period": "Dönem", "totalCiro": "Toplam Ciro (₺)"})
                        fig_trend.update_traces(line_color='#6D28D9')
                        st.plotly_chart(fig_trend, use_container_width=True)
                        if st.button("Kapat"):
                            st.session_state.show_trend = False
                            st.rerun()
        else:
            st.warning("Seçilen dönem için veri bulunamadı veya yüklenemedi.")
else:
    st.error("Dönem listesi alınamadı. Lütfen Google Apps Script bağlantınızı kontrol edin.")
