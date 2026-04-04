import streamlit as st

def load_styles():
    st.markdown("""
    <style>

    /* Background */
    .stApp {
        background: #0a0e27;
    }

    /* Titles */
    h1, h2, h3, h4 {
        color: white !important;
    }

    /* Text */
    p, div, span {
        color: #e2e8f0 !important;
    }

    /* Remove Streamlit default padding */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }

    </style>
    """, unsafe_allow_html=True)
