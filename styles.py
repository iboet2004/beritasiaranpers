import streamlit as st

def apply_custom_styling():
    """
    Apply custom CSS styling to Streamlit app
    """
    st.markdown("""
    <style>
    /* Global Styling */
    .stApp {
        background-color: #f4f4f4;
        font-family: 'Inter', sans-serif;
    }

    /* Metric Cards Styling */
    .metric-container {
        background-color: white;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }

    .metric-container:hover {
        transform: scale(1.02);
    }

    .metric-title {
        color: #555;
        font-size: 0.9em;
        margin-bottom: 5px;
    }

    .metric-value {
        color: #333;
        font-size: 1.5em;
        font-weight: bold;
    }

    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        background-color: white;
        border-radius: 10px;
        padding: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .stTabs [data-baseweb="tab"] {
        transition: all 0.3s ease;
        border-radius: 8px;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background-color: #f0f0f0;
    }

    /* Chart Styling */
    .chart-container {
        background-color: white;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    /* Responsive Design */
    @media (max-width: 768px) {
        .metric-value {
            font-size: 1.2em;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def create_styled_metric(label, value, delta=None):
    """
    Create a styled metric with custom design
    """
    st.markdown(f"""
    <div class="metric-container">
        <div class="metric-title">{label}</div>
        <div class="metric-value">{value}</div>
        {f'<div style="color: {"green" if isinstance(delta, (int, float)) and delta > 0 else "red"}; font-size: 0.8em;">{delta if isinstance(delta, (int, float)) else ""}</div>' if delta is not None else ''}
    </div>
    """, unsafe_allow_html=True)
