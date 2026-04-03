import streamlit as st

def render_signal_card(signal):
    color = "#10b981" if signal['action']=="BUY" else "#ef4444" if signal['action']=="SELL" else "#64748b"

    st.markdown(f"""
    <div style="padding:15px;border-radius:12px;background:{color}20;">
        <h3 style="color:white;">{signal['pair']} — {signal['action']}</h3>
        <p style="color:white;">Score: {signal['score']}</p>
        <p style="color:white;">{', '.join(signal['conditions'])}</p>
    </div>
    """, unsafe_allow_html=True)
