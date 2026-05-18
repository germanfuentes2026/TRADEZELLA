import streamlit as st

st.set_page_config(
    page_title="Trading Journal",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from db import init_db
init_db()

from styles import inject_css
inject_css()

import pandas as pd
from db import get_all_trades
from metrics import compute_metrics
import plotly.graph_objects as go
import plotly.express as px

st.title("📈 Trading Journal — Dashboard")

trades_df = get_all_trades()
metrics = compute_metrics(trades_df)

c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("P&L Neto", f"${metrics['net_pnl']:,.2f}")
c2.metric("Win Rate", f"{metrics['win_rate']:.1f}%")
c3.metric("Profit Factor", f"{metrics['profit_factor']:.2f}" if metrics['profit_factor'] != float('inf') else "∞")
c4.metric("Avg Ganancia", f"${metrics['avg_win']:.2f}")
c5.metric("Avg Pérdida", f"${metrics['avg_loss']:.2f}")
c6.metric("Total Trades", str(metrics["total_trades"]))

st.markdown("---")

if trades_df.empty:
    st.info("🚀 Sin trades aún. Usá el menú lateral para ir al Calendario y cargar tu primera operación.")
else:
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("Equity Curve")
        df_sorted = trades_df.sort_values("date")
        df_sorted["cumulative_pnl"] = df_sorted["pnl"].cumsum()
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_sorted["date"], y=df_sorted["cumulative_pnl"],
            mode="lines+markers", line=dict(color="#378ADD", width=2),
            fill="tozeroy", fillcolor="rgba(55,138,221,0.08)"
        ))
        fig.update_layout(
            height=280, margin=dict(l=0, r=0, t=10, b=0),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.subheader("Distribución P&L")
        fig2 = px.histogram(trades_df, x="pnl", nbins=20, color_discrete_sequence=["#378ADD"])
        fig2.update_layout(
            height=280, margin=dict(l=0, r=0, t=10, b=0),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Últimos 10 trades")
    recent = trades_df.sort_values("date", ascending=False).head(10)[
        ["date", "symbol", "side", "qty", "entry", "exit", "pnl", "note"]
    ].copy()
    recent.columns = ["Fecha", "Instrumento", "Dir", "Contratos", "Entrada", "Salida", "P&L", "Nota"]
    st.dataframe(
        recent.style.map(
            lambda v: f"color: {'#1D9E75' if v > 0 else '#D85A30'}" if isinstance(v, (int, float)) else "",
            subset=["P&L"]
        ).format({"P&L": "${:.2f}", "Entrada": "{:.2f}", "Salida": "{:.2f}"}),
        use_container_width=True,
        hide_index=True,
    )
