```python
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt

def create_top_entities_chart(df, entity_col, top_n=10, title='Top Entitas'):
    """
    Buat chart top entitas
    """
    # Proses entitas
    all_entities = df[entity_col].dropna().str.split(';').explode()
    entity_counts = all_entities.value_counts().head(top_n)
    
    # Buat bar chart dengan Plotly
    fig = px.bar(
        x=entity_counts.index, 
        y=entity_counts.values,
        title=title,
        labels={'x': 'Entitas', 'y': 'Frekuensi'}
    )
    
    fig.update_layout(
        xaxis_title='Entitas',
        yaxis_title='Frekuensi',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_timeline_chart(df, title_col, date_col, title='Timeline'):
    """
    Buat timeline chart untuk publikasi
    """
    # Konversi kolom tanggal
    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    
    # Group by date
    timeline_data = df.groupby(df[date_col].dt.date).size().reset_index()
    timeline_data.columns = [date_col, 'Jumlah']
    
    # Buat line chart
    fig = px.line(
        timeline_data, 
        x=date_col, 
        y='Jumlah',
        title=title
    )
    
    fig.update_layout(
        xaxis_title='Tanggal',
        yaxis_title='Jumlah Publikasi',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_wordcloud(df, text_col, title='Word Cloud'):
    """
    Buat word cloud dari teks
    """
    # Gabungkan semua teks
    text = ' '.join(df[text_col].dropna())
    
    # Buat wordcloud
    wordcloud = WordCloud(
        width=800, 
        height=400, 
        background_color='white'
    ).generate(text)
    
    # Plot
    plt.figure(figsize=(10,5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title(title)
    
    st.pyplot(plt)
```
