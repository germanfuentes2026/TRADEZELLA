import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="Estadísticas — Trading Journal", layout="wide", page_icon="📊")

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from db import init_db, get_all_trades, get_daily_pnl
from styles import inject_css
from metrics import compute_metrics, compute_monthly_summary

init_db()
inject_css()

st.title("📊 Estadísticas")

df = get_all_trades()

if df.empty:
    st.info("Sin datos todavía. Cargá tus primeros trades en el Calendario.")
    st.stop()

df["date"] = pd.to_datetime(df["date"])
m = compute_metrics(df)

st.subheader("Resumen general")
k1, k2, k3, k4 = st.columns(4)
k1.metric("P&L Neto", f"${m['net_pnl']:,.2f}")
k2.metric("Win Rate", f"{m['win_rate']:.1f}%")
k3.metric("Profit Factor", f"{m['profit_factor']:.2f}" if m['profit_factor'] != float('inf') else "∞")
k4.metric("Expectancy por trade", f"${m['expectancy']:.2f}")

k5, k6, k7, k8 = st.columns(4)
k5.metric("Mejor trade", f"${m['best_trade']:,.2f}")
k6.metric("Peor trade", f"${m['worst_trade']:,.2f}")
k7.metric("Max Drawdown", f"${m['max_drawdown']:,.2f}")
k8.metric("Racha ganadora máx.", f"{m['consecutive_wins']} trades")

st.markdown("---")

st.subheader("Equity Curve")
df_sorted = df.sort_values("date").copy()
df_sorted["cumulative_pnl"] = df_sorted["pnl"].cumsum()
df_sorted["trade_num"] = range(1, len(df_sorted) + 1)

fig_eq = go.Figure()
fig_eq.add_trace(go.Scatter(
    x=df_sorted["trade_num"], y=df_sorted["cumulative_pnl"],
    mode="lines", line=dict(color="#378ADD", width=2),
    fill="tozeroy", fillcolor="rgba(55,138,221,0.07)",
    name="Equity acumulada"
))
fig_eq.update_layout(
    height=300, margin=dict(l=0,r=0,t=10,b=0),
    xaxis_title="Nº trade", yaxis_title="P&L acumulado ($)",
    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    yaxis=dict(gridcolor="rgba(128,128,128,0.1)"),
    xaxis=dict(gridcolor="rgba(0,0,0,0)"),
    showlegend=False
)
st.plotly_chart(fig_eq, use_container_width=True)

st.subheader("P&L diario")
daily = get_daily_pnl()
if not daily.empty:
    daily["color"] = daily["daily_pnl"].apply(lambda x: "#1D9E75" if x >= 0 else "#D85A30")
    fig_daily = go.Figure(go.Bar(
        x=daily["date"], y=daily["daily_pnl"],
        marker_color=daily["color"],
        text=daily["daily_pnl"].apply(lambda x: f"${x:+,.0f}"),
        textposition="outside"
    ))
    fig_daily.update_layout(
        height=280, margin=dict(l=0,r=0,t=20,b=0),
        plot_bgcolor="rgba(0,0,0,0)",
