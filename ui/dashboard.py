import streamlit as st

def render_signal_card(signal):
    """
    UI PRO per segnali istituzionali.
    """

    pair = signal["pair"]
    action = signal["action"]
    score = signal["score"]
    conditions = signal["conditions"]

    # Colori dinamici
    if action == "BUY":
        color = "#10b981"   # verde
    elif action == "SELL":
        color = "#ef4444"   # rosso
    elif action == "WEAK":
        color = "#f59e0b"   # giallo
    else:
        color = "#64748b"   # grigio

    # CARD
    st.markdown(f"""
    <div style="
        background-color: {color}20;
        border-left: 6px solid {color};
        padding: 18px;
        border-radius: 12px;
        margin-bottom: 20px;
    ">
        <h2 style="color:white; margin:0; padding:0;">
            {pair} — <span style="color:{color};">{action}</span>
        </h2>

        <h3 style="color:white; margin-top:5px;">
            Score: <span style="color:{color};">{score}/100</span>
        </h3>
    """, unsafe_allow_html=True)

    # SEZIONE DETTAGLI
    st.markdown("""
    <div style="margin-top:15px;">
        <h4 style="color:#a5b4fc;">📌 Condizioni soddisfatte</h4>
    </div>
    """, unsafe_allow_html=True)

    for cond in conditions:
        st.markdown(f"""
        <div style="
            background:#1e293b;
            padding:8px 12px;
            border-radius:8px;
            margin-bottom:6px;
            color:#e2e8f0;
        ">
            • {cond}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
