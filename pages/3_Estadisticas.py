import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Estadisticas", layout="wide", page_icon="📊")

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from db import init_db, get_all_trades, get_daily_pnl
from styles import inject_css
from metrics import compute_metrics, compute_monthly_summary

init_db()
inject_css()

st.title("Estadisticas")

df = get_all_trades()

if df.empty:
    st.info("Sin datos todavia.")
    st.stop()

df["date"] = pd.to_datetime(df["date"])
m = compute_metrics(df)

k1, k2, k3, k4 = st.columns(4)
k1.metric("P&L Neto", f"${m['net_pnl']:,.2f}")
k2.metric("Win Rate", f"{m['win_rate']:.1f}%")
k3.metric("Profit Factor", f"{m['profit_factor']:.2f}" if m['profit_factor'] != float('inf') else "inf")
k4.metric("Expectancy", f"${m['expectancy']:.2f}")

k5, k6, k7, k8 = st.columns(4)
k5.metric("Mejor trade", f"${m['best_trade']:,.2f}")
k6.metric("Peor trade", f"${m['worst_trade']:,.2f}")
k7.metric("Max Drawdown", f"${m['max_drawdown']:,.2f}")
k8.metric("Racha ganadora", f"{m['consecutive_wins']} trades")

st.markdown("---")

df_sorted = df.sort_values("date").copy()
df_sorted["cumulative_pnl"] = df_sorted["pnl"].cumsum()
df_sorted["trade_num"] = range(1, len(df_sorted) + 1)

fig_eq = go.Figure()
fig_eq.add_trace(go.Scatter(
    x=df_sorted["trade_num"],
    y=df_sorted["cumulative_pnl"],
    mode="lines",
    line=dict(color="#378ADD", width=2),
    fill="tozeroy"
))
fig_eq.update_layout(height=300, margin=dict(l=0,r=0,t=10,b=0),
    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
st.plotly_chart(fig_eq, use_container_width=True)

daily = get_daily_pnl()
if not daily.empty:
    colors = ["#1D9E75" if x >= 0 else "#D85A30" for x in daily["daily_pnl"]]
    fig_d = go.Figure(go.Bar(x=daily["date"], y=daily["daily_pnl"], marker_color=colors))
    fig_d.update_layout(height=280, margin=dict(l=0,r=0,t=20,b=0),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_d, use_container_width=True)

monthly = compute_monthly_summary(df)
if not monthly.empty:
    st.dataframe(
        monthly[["month","pnl","trades","wins","win_rate"]].rename(
            columns={"month":"Mes","pnl":"P&L","trades":"Trades","wins":"Ganadoras","win_rate":"Win Rate %"}
        ).style.format({"P&L":"${:+,.2f}","Win Rate %":"{:.1f}%"}),
        use_container_width=True, hide_index=True
    )
