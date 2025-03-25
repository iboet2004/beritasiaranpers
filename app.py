import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from data_loader import load_dataset, process_entities, get_unique_locations
from visualization import (
    create_interactive_timeline,
    create_enhanced_wordcloud
)
from filters import create_advanced_filters
from styles import apply_custom_styling, create_styled_metric

# Set page config
st.set_page_config(
    page_title="Dashboard Analisis Siaran Pers",
    page_icon="📊",
    layout="wide"
)

# Apply custom styling
apply_custom_styling()

def create_sp_selector(df_sp, sp_title_col, sp_date_col):
    """
    Create a dropdown selector for press releases with date range filter
    """
    # Add a "Semua Siaran Pers" option
    sp_titles = ["Semua Siaran Pers"] + list(df_sp[sp_title_col].dropna().unique())
    
    # Convert date column to datetime
    df_sp[sp_date_col] = pd.to_datetime(df_sp[sp_date_col], errors='coerce')
    
    # Create columns for date inputs
    col1, col2, col3 = st.columns([2, 2, 3])
    
    with col1:
        start_date = st.date_input(
            "Tanggal Mulai", 
            min_value=df_sp[sp_date_col].min().date(), 
            max_value=df_sp[sp_date_col].max().date(), 
            value=df_sp[sp_date_col].min().date()
        )
    
    with col2:
        end_date = st.date_input(
            "Tanggal Akhir", 
            min_value=df_sp[sp_date_col].min().date(), 
            max_value=df_sp[sp_date_col].max().date(), 
            value=df_sp[sp_date_col].max().date()
        )
    
    with col3:
        selected_sp = st.selectbox(
            "Pilih Siaran Pers", 
            sp_titles, 
            index=0, 
            key="sp_selector"
        )
    
    return selected_sp, start_date, end_date

def filter_dataframe(df, title_col, date_col, selected_title, start_date, end_date):
    """
    Filter dataframe based on selected title and date range
    """
    # Convert columns to datetime if not already
    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    
    # Filter by date range
    df_filtered = df[
        (df[date_col].dt.date >= start_date) & 
        (df[date_col].dt.date <= end_date)
    ]
    
    # Filter by title
    if selected_title == "Semua Siaran Pers":
        return df_filtered
    else:
        return df_filtered[df_filtered[title_col] == selected_title]

def create_sources_trend_analysis(df, entity_col, date_col, selected_sp=None):
    """
    Create scatter plot for sources mentioning trend with improved visualization
    """
    # Filter dataframe if a specific SP is selected
    if selected_sp is not None and selected_sp != "Semua Siaran Pers":
        df = df[df[df.columns[0]] == selected_sp]
    
    # Ensure dataframe is not empty
    if df.empty:
        st.warning("Tidak ada data untuk dianalisis")
        return
    
    # Convert date column
    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    df = df.dropna(subset=[date_col])
    
    # Prepare entity data
    all_entities_data = []
    
    for _, row in df.iterrows():
        date = row[date_col]
        # Split entities separated by semicolon
        entities = row[entity_col].split(';') if pd.notna(row[entity_col]) else []
        
        for entity in entities:
            entity = entity.strip()
            if entity:
                all_entities_data.append({
                    'Narasumber': entity,
                    'Tanggal': date
                })
    
    # Create DataFrame
    if not all_entities_data:
        st.warning("Tidak ada narasumber yang ditemukan")
        return
    
    entities_df = pd.DataFrame(all_entities_data)
    
    # Agregasi per minggu dengan datetime
    def get_week_start(date):
        return date - pd.Timedelta(days=date.weekday())
    
    entities_df['Minggu'] = entities_df['Tanggal'].apply(get_week_start)
    
    # Group by week and count
    weekly_counts = entities_df.groupby(['Narasumber', 'Minggu']).size().reset_index(name='Frekuensi')
    
    # Tambahkan rentang tanggal minggu
    def get_week_range(week_start):
        end = week_start + pd.Timedelta(days=6)
        return f"{week_start.day}-{end.day} {week_start.strftime('%B %Y')}"
    
    weekly_counts['RentangMinggu'] = weekly_counts['Minggu'].apply(get_week_range)
    
    # Count total frequencies
    narasumber_counts = weekly_counts.groupby('Narasumber')['Frekuensi'].sum().sort_values(ascending=False)
    
    # Select top 10 sources for visualization
    top_sources = narasumber_counts.head(10)

    # Prepare data for top sources
    if not top_sources.empty:
        plot_data = weekly_counts[weekly_counts['Narasumber'].isin(top_sources.index)]
    else:
        plot_data = weekly_counts.copy()  # Pakai semua data kalau tidak ada top sources
    
    # Metrics with custom styling
    col1, col2, col3 = st.columns(3)
    
    with col1:
        create_styled_metric("Total Siaran Pers", len(df))
    
    with col2:
        create_styled_metric("Total Narasumber", len(narasumber_counts))
    
    with col3:
        top_narasumber = top_sources.index[0]
        top_narasumber_count = top_sources.iloc[0]
        create_styled_metric("Narasumber Tersering", f"{top_narasumber}", f"({top_narasumber_count} kali)")
    
    # Create scatter plot with Plotly
    fig = px.scatter(
        plot_data, 
        x='Minggu', 
        y='Narasumber',
        color='Narasumber',
        size='Frekuensi',
        size_max=20,
        title='Tren Penyebutan Narasumber',
        labels={'Narasumber': 'Narasumber', 'Minggu': 'Minggu'},
        height=400,
        custom_data=['Narasumber', 'RentangMinggu', 'Frekuensi']
    )
    
    # Customize hover template
    fig.update_traces(
        hovertemplate='<b>%{customdata[0]}</b><br>%{customdata[1]}<br>Frekuensi: %{customdata[2]} kali<extra></extra>',
        marker=dict(
            line=dict(width=1, color='DarkSlateGrey'),
            opacity=0.7
        )
    )
    
    # Customize layout
    fig.update_layout(
        yaxis={
            'categoryorder':'total ascending',
            'tickfont': dict(size=10)
        },
        xaxis_title="Pekan",
        yaxis_title="Narasumber",
        showlegend=False,
        title_font_size=16,
        plot_bgcolor='rgba(240,240,240,0.1)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    st.plotly_chart(fig, use_container_width=True)

def main():
    # Title with custom styling
    st.markdown("# Dashboard Analisis Siaran Pers", unsafe_allow_html=True)
    
    # Load data
    with st.spinner("Memuat data..."):
        df_sp = load_dataset("DATASET SP")
        df_berita = load_dataset("DATASET BERITA")
    
    if df_sp.empty and df_berita.empty:
        st.error("Gagal memuat data")
        return
    
    # Column definitions
    sp_title_col = df_sp.columns[0]
    sp_content_col = df_sp.columns[1]
    sp_sources_col = df_sp.columns[3]
    sp_date_col = df_sp.columns[4]

    # Konversi kolom tanggal ke format datetime dengan error handling
    df_sp[sp_date_col] = pd.to_datetime(df_sp[sp_date_col], errors='coerce')

    # Pastikan tidak semua data NaT
    if df_sp[sp_date_col].isna().all():
        st.error("Semua data di kolom PUBLIKASI tidak valid atau kosong!")
        st.stop()

    # Add advanced filtering
    filtered_df_sp = create_advanced_filters(df_sp)
    filtered_df_berita = create_advanced_filters(df_berita)

    
    # Create tabs with improved styling
    tab1, tab2, tab3 = st.tabs(["🗒️ Siaran Pers", "📰 Pemberitaan", "🔍 Analisis Mendalam"])
    
    # Tab 1: Siaran Pers
    with tab1:
        # Selector for press releases with date range
        selected_sp, start_date, end_date = create_sp_selector(df_sp, sp_title_col, sp_date_col)
        
        # Filter dataframe with date range
        df_sp_filtered = filter_dataframe(
            df_sp, 
            sp_title_col, 
            sp_date_col, 
            selected_sp, 
            start_date, 
            end_date
        )
        
        # Trend Penyebutan Narasumber
        st.markdown("## Trend Penyebutan Narasumber", unsafe_allow_html=True)
        create_sources_trend_analysis(
            df_sp, 
            sp_sources_col, 
            sp_date_col, 
            selected_sp
        )
        
        # Timeline Produksi Siaran Pers
        st.markdown("## Timeline Produksi Siaran Pers", unsafe_allow_html=True)
        create_timeline_chart(
            df_sp_filtered, 
            sp_title_col, 
            sp_date_col, 
            "Publikasi Siaran Pers"
        )
    
    # Placeholder for other tabs
    with tab2:
        st.write("Pemberitaan - Dalam Pengembangan")
    
    with tab3:
        st.write("Analisis Mendalam - Dalam Pengembangan")

if __name__ == "__main__":
    main()
