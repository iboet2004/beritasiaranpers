import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import numpy as np
from utils import clean_text, get_stopwords

def create_scorecard(value, label):
    """
    Create a simple scorecard metric
    """
    st.metric(label, value)

def create_top_entities_chart(data, title, top_n=10):
    """
    Create bar chart for top entities
    """
    fig = px.bar(
        x=data.index, 
        y=data.values, 
        title=title,
        labels={'x': 'Entitas', 'y': 'Jumlah'}
    )
    st.plotly_chart(fig, use_container_width=True)

def create_timeline_chart(df, title_col, date_col, chart_title):
    """
    Create timeline chart for dates
    """
    # Convert date column to datetime
    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    
    # Group by date and count
    timeline_data = df.groupby(df[date_col].dt.date).size().reset_index()
    timeline_data.columns = [date_col, 'Jumlah']
    
    fig = px.line(
        timeline_data, 
        x=date_col, 
        y='Jumlah', 
        title=chart_title
    )
    st.plotly_chart(fig, use_container_width=True)

def create_wordcloud(text_series, title):
    """
    Create word cloud from text series
    """
    # Combine all text
    text = ' '.join(text_series.dropna().astype(str))
    
    # Generate word cloud
    wordcloud = WordCloud(
        width=800, 
        height=400, 
        background_color='white'
    ).generate(text)
    
    # Display word cloud
    plt.figure(figsize=(10,5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title(title)
    st.pyplot(plt)

def create_side_by_side_wordclouds(series1, series2, title1, title2):
    """
    Create two word clouds side by side
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16,8))
    
    # Word cloud 1
    text1 = ' '.join(series1.dropna().astype(str))
    wordcloud1 = WordCloud(width=400, height=200, background_color='white').generate(text1)
    ax1.imshow(wordcloud1, interpolation='bilinear')
    ax1.set_title(title1)
    ax1.axis('off')
    
    # Word cloud 2
    text2 = ' '.join(series2.dropna().astype(str))
    wordcloud2 = WordCloud(width=400, height=200, background_color='white').generate(text2)
    ax2.imshow(wordcloud2, interpolation='bilinear')
    ax2.set_title(title2)
    ax2.axis('off')
    
    plt.tight_layout()
    st.pyplot(fig)

def create_advanced_bar_chart(data, title, x_label='Entitas', y_label='Jumlah', top_n=10, color_scale='Viridis'):
    """
    Create an enhanced bar chart with more interactive features
    """
    # Ambil top N data
    top_data = data.nlargest(top_n)
    
    # Buat figure dengan Plotly
    fig = px.bar(
        x=top_data.index, 
        y=top_data.values,
        title=title,
        labels={'x': x_label, 'y': y_label},
        color=top_data.values,
        color_continuous_scale=color_scale
    )
    
    # Kustomisasi layout
    fig.update_layout(
        plot_bgcolor='rgba(240,240,240,0.1)',
        paper_bgcolor='rgba(0,0,0,0)',
        title_font_size=16,
        height=400,
        xaxis_tickangle=-45
    )
    
    # Tambahkan hover template
    fig.update_traces(
        hovertemplate='<b>%{x}</b><br>%{y} entitas<extra></extra>',
        marker_line_color='rgb(50,50,50)',
        marker_line_width=1.5
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_interactive_timeline(df, date_col, value_col=None, title='Timeline', rolling_window=7):
    """
    Create an interactive timeline with rolling average
    """
    # Pastikan kolom tanggal adalah datetime
    df[date_col] = pd.to_datetime(df[date_col])
    
    # Jika tidak ada value_col, gunakan ukuran
    if value_col is None:
        timeline_data = df.groupby(df[date_col].dt.date).size().reset_index()
        timeline_data.columns = [date_col, 'Jumlah']
    else:
        timeline_data = df.groupby(df[date_col].dt.date)[value_col].sum().reset_index()
    
    # Hitung rata-rata bergerak
    timeline_data['Rolling_Average'] = timeline_data['Jumlah'].rolling(window=rolling_window, min_periods=1).mean()
    
    # Buat figure
    fig = go.Figure()
    
    # Tambahkan bar chart
    fig.add_trace(go.Bar(
        x=timeline_data[date_col], 
        y=timeline_data['Jumlah'],
        name='Harian',
        marker_color='rgba(58, 71, 80, 0.6)',
        hovertemplate='Tanggal: %{x}<br>Jumlah: %{y}<extra></extra>'
    ))
    
    # Tambahkan garis rata-rata bergerak
    fig.add_trace(go.Scatter(
        x=timeline_data[date_col], 
        y=timeline_data['Rolling_Average'],
        mode='lines',
        name=f'Rata-rata {rolling_window} Hari',
        line=dict(color='red', width=3)
    ))
    
    # Kustomisasi layout
    fig.update_layout(
        title=title,
        xaxis_title='Tanggal',
        yaxis_title='Jumlah',
        height=400,
        plot_bgcolor='rgba(240,240,240,0.1)',
        paper_bgcolor='rgba(0,0,0,0)',
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_enhanced_wordcloud(text_series, title, width=800, height=400):
    """
    Create a more advanced wordcloud with custom processing
    """
    # Gabungkan teks dan bersihkan
    stop_words = get_stopwords()
    
    # Proses teks
    processed_texts = text_series.apply(clean_text)
    full_text = ' '.join(processed_texts.dropna())
    
    # Filter stopwords
    words = full_text.split()
    filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
    filtered_text = ' '.join(filtered_words)
    
    # Generate wordcloud
    wordcloud = WordCloud(
        width=width, 
        height=height, 
        background_color='white',
        colormap='viridis',  # Warna gradien
        max_words=100,
        min_font_size=10
    ).generate(filtered_text)
    
    # Plot
    plt.figure(figsize=(15,8))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title(title, fontsize=16, pad=20)
    
    st.pyplot(plt)

def create_entity_network(df, entity_col, connection_col):
    """
    Create a network graph of entities
    """
    import networkx as nx
    
    # Buat graph
    G = nx.Graph()
    
    # Proses data untuk mencari koneksi
    for _, row in df.iterrows():
        entities = str(row[entity_col]).split(';')
        connection = row[connection_col]
        
        # Tambahkan node dan edge
        for entity in entities:
            G.add_node(entity.strip())
            G.add_edge(entity.strip(), connection)
    
    # Visualisasi
    plt.figure(figsize=(15,10))
    pos = nx.spring_layout(G, k=0.5)  # positions for all nodes
    
    # Nodes
    nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=50, alpha=0.8)
    
    # Edges
    nx.draw_networkx_edges(G, pos, width=0.5, alpha=0.5)
    
    # Labels
    nx.draw_networkx_labels(G, pos, font_size=8, font_family='sans-serif')
    
    plt.title("Jaringan Entitas")
    plt.axis('off')
    
    st.pyplot(plt)
