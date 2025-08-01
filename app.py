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
    page_icon="📊",
    layout="wide"
)

# Google Apps Script URL'niz
APPS_SCRIPT_URL = 'https://script.google.com/macros/s/AKfycbxSquBU2QkyB79SkPSPHPd7BKJfiJZB3su85LosK7YBcRe4vdrrAAczgp3LOuCC76Xp7A/exec'

# -----------------------------------------------------------------------------
# Veri Çekme ve İşleme Fonksiyonları
# -----------------------------------------------------------------------------

@st.cache_data(ttl=600)  # Veriyi 10 dakika boyunca önbellekte tut
def fetch_data(action, params=None):
    """Google Apps Script'ten veri çeker."""
    if params is None:
        params = {}
    
    # Her istekte önbelleği atlatmak için zaman damgası ekle
    params['t'] = datetime.now().timestamp()
    
    try:
        response = requests.get(f"{APPS_SCRIPT_URL}?action={action}", params=params)
        response.raise_for_status()  # HTTP hatalarını yakala
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
# Ana Arayüz
# -----------------------------------------------------------------------------

# --- Başlık ---
col1, col2 = st.columns([1, 10])
with col1:
    st.image("https://static.ticimax.cloud/32769/uploads/editoruploads/hedef-image/logo.png", width=70)
with col2:
    st.title("Hedef AVM Online Satış İstatistik")

# --- Filtreler ---
periods_data = fetch_data('getAvailablePeriods')
if periods_data and periods_data.get('periods'):
    month_order = ['OCAK', 'ŞUBAT', 'MART', 'NİSAN', 'MAYIS', 'HAZİRAN', 'TEMMUZ', 'AĞUSTOS', 'EYLÜL', 'EKİM', 'KASIM', 'ARALIK']
    
    def get_period_sort_key(period_string):
        """Dönem adlarını güvenli bir şekilde sıralamak için anahtar oluşturur."""
        try:
            parts = period_string.split(' ')
            if len(parts) == 2:
                month = parts[0].upper()
                year = int(parts[1])
                if month in month_order:
                    return (year, month_order.index(month))
        except (ValueError, IndexError):
            pass
        return (0, 0) # Sıralanamayanlar en sona gider

    periods = sorted(
        periods_data['periods'],
        key=get_period_sort_key,
        reverse=True
    )
    
    selected_period = st.selectbox(
        "**Dönem Seçimi**",
        periods,
        label_visibility="collapsed"
    )
    
    st.markdown(f"**{selected_period}** Dönemi Analizi")
    st.markdown("---")

    # --- Veri Yükleme ve Gösterge Paneli ---
    if selected_period:
        data = fetch_data('getLeaderboard', {'sheetName': selected_period})
        
        if data and data.get('leaderboard'):
            df_leaderboard = pd.DataFrame(data['leaderboard'])
            df_raw_sales = pd.DataFrame(data['rawSales'])

            # Sayısal olmayan değerleri 0 yap
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

            metric_col1, metric_col2, metric_col3 = st.columns(3)
            metric_col1.metric(label="Dönem Toplam Ciro", value=format_currency(total_ciro))
            metric_col2.metric(label="Toplam Satış Adedi", value=f"{int(total_sales_count)}")
            metric_col3.metric(label="Ortalama Satış Tutarı", value=format_currency(avg_sale_amount))
            
            st.markdown("---")

            # --- Şube ve Kategori Analizi ---
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Şubeler Ciro Karşılaştırması")
                if not df_leaderboard.empty and df_leaderboard['totalCiro'].sum() > 0:
                    df_sorted = df_leaderboard.sort_values("totalCiro", ascending=True)
                    fig = px.bar(
                        df_sorted,
                        x="totalCiro",
                        y="branch",
                        orientation='h',
                        text_auto='.2s',
                        labels={"totalCiro": "Toplam Ciro (₺)", "branch": "Şube"}
                    )
                    fig.update_traces(textposition='outside')
                    fig.update_layout(yaxis_title=None, xaxis_title=None, showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Bu dönem için şube ciro verisi bulunamadı.")

            with col2:
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

            # --- Aylık Trend Butonu ve Grafiği ---
            st.markdown("---")
            if st.button("Aylık Trendi Görüntüle"):
                trend_data = fetch_data('getMonthlyTrendData')
                if trend_data:
                    df_trend = pd.DataFrame(trend_data)
                    df_trend['totalCiro'] = pd.to_numeric(df_trend['totalCiro'], errors='coerce').fillna(0)
                    
                    df_trend['sort_key'] = df_trend['period'].apply(get_period_sort_key)
                    df_trend = df_trend.sort_values('sort_key').reset_index(drop=True)

                    st.subheader("Aylık Ciro Trendi")
                    fig_trend = px.line(
                        df_trend,
                        x='period',
                        y='totalCiro',
                        markers=True,
                        labels={"period": "Dönem", "totalCiro": "Toplam Ciro (₺)"}
                    )
                    st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.warning("Seçilen dönem için veri bulunamadı veya yüklenemedi.")
else:
    st.error("Dönem listesi alınamadı. Lütfen Google Apps Script bağlantınızı kontrol edin.")
