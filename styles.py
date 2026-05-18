import streamlit as st


def inject_css():
    st.markdown("""
    <style>
        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: #0f1117;
        }
        [data-testid="stSidebar"] * {
            color: #e0e0e0 !important;
        }

        /* Metric cards */
        [data-testid="stMetric"] {
            background: #1a1d27;
            border: 1px solid #2a2d3a;
            border-radius: 10px;
            padding: 12px 16px;
        }
        [data-testid="stMetricLabel"] p {
            font-size: 12px !important;
            color: #888 !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        [data-testid="stMetricValue"] {
            font-size: 22px !important;
            font-weight: 600 !important;
        }

        /* Calendar day cells */
        .cal-day {
            border: 1px solid #2a2d3a;
            border-radius: 8px;
            padding: 8px;
            min-height: 80px;
            cursor: pointer;
            transition: border-color 0.15s;
            background: #1a1d27;
        }
        .cal-day:hover { border-color: #378ADD; }
        .cal-day-profit { background: rgba(29,158,117,0.08) !important; border-color: rgba(29,158,117,0.3) !important; }
        .cal-day-loss { background: rgba(216,90,48,0.08) !important; border-color: rgba(216,90,48,0.3) !important; }
        .cal-day-today { border-color: #378ADD !important; border-width: 2px !important; }
        .cal-day-num { font-size: 12px; color: #666; font-weight: 500; }
        .cal-pnl-pos { color: #1D9E75; font-weight: 600; font-size: 14px; margin-top: 4px; }
        .cal-pnl-neg { color: #D85A30; font-weight: 600; font-size: 14px; margin-top: 4px; }
        .cal-meta { font-size: 10px; color: #666; margin-top: 2px; }
        .cal-header { text-align: center; font-size: 11px; color: #555; font-weight: 500;
                      text-transform: uppercase; padding: 4px 0; letter-spacing: 0.06em; }

        /* Buttons */
        .stButton > button {
            border-radius: 8px;
            font-weight: 500;
        }

        /* Trade side badges */
        .badge-long {
            background: rgba(29,158,117,0.15);
            color: #1D9E75;
            padding: 2px 8px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 600;
        }
        .badge-short {
            background: rgba(216,90,48,0.15);
            color: #D85A30;
            padding: 2px 8px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 600;
        }

        /* Positive / negative colors */
        .pos { color: #1D9E75 !important; }
        .neg { color: #D85A30 !important; }

        /* Hide streamlit default elements */
        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }
        header { visibility: hidden; }

        /* Form inputs */
        .stTextInput input, .stNumberInput input, .stSelectbox select, .stTextArea textarea {
            border-radius: 8px !important;
            border: 1px solid #2a2d3a !important;
            background: #1a1d27 !important;
        }

        /* Dataframe */
        [data-testid="stDataFrame"] {
            border-radius: 10px;
            overflow: hidden;
            border: 1px solid #2a2d3a;
        }

        /* Page title */
        h1 { font-size: 26px !important; font-weight: 600 !important; }
        h2 { font-size: 20px !important; font-weight: 500 !important; }
        h3 { font-size: 16px !important; font-weight: 500 !important; }

        /* Info/success/error boxes */
        .stAlert { border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)
