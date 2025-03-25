import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from utils import clean_text, get_stopwords

def create_top_entities_chart(data, title, top_n=10, color_scale='Viridis'):
    """
    Create a top entities bar chart
    
    Args:
        data (pd.Series): Series with entity counts
        title (str): Chart title
        top_n (int): Number of top entities to show
        color_scale (str): Color scale for chart
    """
    # Use existing nlargest and bar chart logic
    top_data = data.nlargest(top_n)
    
    fig = px.bar(
        x=top_data.index, 
        y=top_data.values,
        title=title,
        labels={'x': 'Entitas', 'y': 'Jumlah'},
        color=top_data.values,
        color_continuous_scale=color_scale
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(240,240,240,0.1)',
        paper_bgcolor='rgba(0,0,0,0)',
        title_font_size=16,
        height=400,
        xaxis_tickangle=-45
    )
    
    fig.update_traces(
        hovertemplate='<b>%{x}</b><br>%{y} entitas<extra></extra>',
        marker_line_color='rgb(50,50,50)',
        marker_line_width=1.5
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_timeline_chart(df, title_col, date_col, chart_title):
    """
    Create an interactive timeline chart
    
    Args:
        df (pd.DataFrame): Input dataframe
        title_col (str): Column with titles
        date_col (str): Column with dates
        chart_title (str): Chart title
    """
    # Convert date column to datetime
    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    
    # Group by date and count
    timeline_data = df.groupby(df[date_col].dt.date).size().reset_index()
    timeline_data.columns = [date_col, 'Jumlah']
    
    # Create line chart
    fig = go.Figure(data=[
        go.Scatter(
            x=timeline_data[date_col], 
            y=timeline_data['Jumlah'],
            mode='lines+markers',
            name='Publikasi',
            line=dict(color='blue', width=2),
            marker=dict(size=8)
        )
    ])
    
    fig.update_layout(
        title=chart_title,
        xaxis_title='Tanggal',
        yaxis_title='Jumlah Publikasi',
        height=400,
        plot_bgcolor='rgba(240,240,240,0.1)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_wordcloud(text_series, title):
    """
    Create a wordcloud from text series
    
    Args:
        text_series (pd.Series): Series of text
        title (str): Wordcloud title
    """
    # Combine text and clean
    stop_words = get_stopwords()
    
    # Process text
    processed_texts = text_series.apply(clean_text)
    full_text = ' '.join(processed_texts.dropna())
    
    # Filter stopwords
    words = full_text.split()
    filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
    filtered_text = ' '.join(filtered_words)
    
    # Generate wordcloud
    wordcloud = WordCloud(
        width=800, 
        height=400, 
        background_color='white',
        colormap='viridis',
        max_words=100,
        min_font_size=10
    ).generate(filtered_text)
    
    # Plot
    plt.figure(figsize=(15,8))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title(title, fontsize=16, pad=20)
    
    st.pyplot(plt)
