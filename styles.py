import streamlit as st


def inject_css():
    st.markdown("""
    <style>
        /* ── Fondo general ── */
        [data-testid="stAppViewContainer"] {
            background-color: #f5f6fa;
        }
        [data-testid="stMain"] {
            background-color: #f5f6fa;
        }

        /* ── Sidebar ── */
        [data-testid="stSidebar"] {
            background-color: #1e2130;
        }
        [data-testid="stSidebar"] * {
            color: #e0e0e0 !important;
        }

        /* ── Metric cards — fondo blanco ── */
        [data-testid="stMetric"] {
            background: #ffffff;
            border: 1px solid #e2e5ef;
            border-radius: 10px;
            padding: 12px 16px;
            box-shadow: 0 1px 4px rgba(0,0,0,0.06);
        }
        [data-testid="stMetricLabel"] p {
            font-size: 12px !important;
            color: #6b7280 !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        [data-testid="stMetricValue"] {
            font-size: 22px !important;
            font-weight: 600 !important;
            color: #111827 !important;
        }

        /* ── Calendar day cells ── */
        .cal-day {
            border: 1px solid #e2e5ef;
            border-radius: 8px;
            padding: 8px;
            min-height: 80px;
            cursor: pointer;
            transition: border-color 0.15s;
            background: #ffffff;
        }
        .cal-day:hover { border-color: #378ADD; }
        .cal-day-profit { background: rgba(29,158,117,0.08) !important; border-color: rgba(29,158,117,0.3) !important; }
        .cal-day-loss   { background: rgba(216,90,48,0.08)  !important; border-color: rgba(216,90,48,0.3)  !important; }
        .cal-day-today  { border-color: #378ADD !important; border-width: 2px !important; }
        .cal-day-num    { font-size: 12px; color: #9ca3af; font-weight: 500; }
        .cal-pnl-pos    { color: #1D9E75; font-weight: 600; font-size: 14px; margin-top: 4px; }
        .cal-pnl-neg    { color: #D85A30; font-weight: 600; font-size: 14px; margin-top: 4px; }
        .cal-meta       { font-size: 10px; color: #9ca3af; margin-top: 2px; }
        .cal-header     { text-align: center; font-size: 11px; color: #6b7280; font-weight: 500;
                          text-transform: uppercase; padding: 4px 0; letter-spacing: 0.06em; }

        /* ── Buttons ── */
        .stButton > button {
            border-radius: 8px;
            font-weight: 500;
        }

        /* ── Trade side badges ── */
        .badge-long {
            background: rgba(29,158,117,0.12);
            color: #1D9E75;
            padding: 2px 8px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 600;
        }
        .badge-short {
            background: rgba(216,90,48,0.12);
            color: #D85A30;
            padding: 2px 8px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 600;
        }

        /* ── Positive / negative colors ── */
        .pos { color: #1D9E75 !important; }
        .neg { color: #D85A30 !important; }

        /* ── Hide streamlit default elements ── */
        #MainMenu { visibility: hidden; }
        footer    { visibility: hidden; }
        header    { visibility: hidden; }

        /* ── Form inputs — fondo blanco ── */
        .stTextInput input,
        .stNumberInput input,
        .stSelectbox select,
        .stTextArea textarea {
            border-radius: 8px !important;
            border: 1px solid #d1d5db !important;
            background: #ffffff !important;
            color: #111827 !important;
        }

        /* ── Dataframe ── */
        [data-testid="stDataFrame"] {
            border-radius: 10px;
            overflow: hidden;
            border: 1px solid #e2e5ef;
            background: #ffffff;
        }

        /* ── Page titles ── */
        h1 { font-size: 26px !important; font-weight: 600 !important; color: #111827 !important; }
        h2 { font-size: 20px !important; font-weight: 500 !important; color: #1f2937 !important; }
        h3 { font-size: 16px !important; font-weight: 500 !important; color: #1f2937 !important; }

        /* ── Info/success/error boxes ── */
        .stAlert { border-radius: 10px; }

        /* ── Expanders — fondo blanco ── */
        [data-testid="stExpander"] {
            background: #ffffff;
            border: 1px solid #e2e5ef;
            border-radius: 10px;
        }
    </style>
    """, unsafe_allow_html=True)
