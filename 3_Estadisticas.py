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

# ── Full KPIs ────────────────────────────────────────────────────────────────
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

# ── Equity Curve ─────────────────────────────────────────────────────────────
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

# ── P&L by day ───────────────────────────────────────────────────────────────
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
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(gridcolor="rgba(128,128,128,0.1)"),
        xaxis=dict(gridcolor="rgba(0,0,0,0)"),
        showlegend=False
    )
    st.plotly_chart(fig_daily, use_container_width=True)

col1, col2 = st.columns(2)

# ── P&L distribution ──────────────────────────────────────────────────────────
with col1:
    st.subheader("Distribución de P&L")
    fig_hist = go.Figure()
    wins_data = df[df["pnl"] > 0]["pnl"]
    loss_data = df[df["pnl"] < 0]["pnl"]
    if len(wins_data) > 0:
        fig_hist.add_trace(go.Histogram(x=wins_data, name="Ganadoras", marker_color="#1D9E75", opacity=0.75))
    if len(loss_data) > 0:
        fig_hist.add_trace(go.Histogram(x=loss_data, name="Perdedoras", marker_color="#D85A30", opacity=0.75))
    fig_hist.update_layout(
        height=260, margin=dict(l=0,r=0,t=10,b=0), barmode="overlay",
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="top", y=1.1)
    )
    st.plotly_chart(fig_hist, use_container_width=True)

# ── Win/Loss by instrument ────────────────────────────────────────────────────
with col2:
    st.subheader("P&L por instrumento")
    by_sym = df.groupby("symbol").agg(
        pnl=("pnl", "sum"),
        trades=("pnl", "count"),
        wins=("pnl", lambda x: (x > 0).sum())
    ).reset_index()
    by_sym["win_rate"] = (by_sym["wins"] / by_sym["trades"] * 100).round(1)
    by_sym["color"] = by_sym["pnl"].apply(lambda x: "#1D9E75" if x >= 0 else "#D85A30")
    fig_sym = go.Figure(go.Bar(
        y=by_sym["symbol"], x=by_sym["pnl"],
        orientation="h",
        marker_color=by_sym["color"],
        text=by_sym["pnl"].apply(lambda x: f"${x:+,.0f}"),
        textposition="outside"
    ))
    fig_sym.update_layout(
        height=260, margin=dict(l=0,r=0,t=10,b=0),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(gridcolor="rgba(128,128,128,0.1)"),
        yaxis=dict(gridcolor="rgba(0,0,0,0)"),
        showlegend=False
    )
    st.plotly_chart(fig_sym, use_container_width=True)

# ── Monthly summary ───────────────────────────────────────────────────────────
st.subheader("Resumen mensual")
monthly = compute_monthly_summary(df)
if not monthly.empty:
    monthly["color"] = monthly["pnl"].apply(lambda x: "#1D9E75" if x >= 0 else "#D85A30")
    fig_month = go.Figure(go.Bar(
        x=monthly["month"], y=monthly["pnl"],
        marker_color=monthly["color"],
        text=monthly["pnl"].apply(lambda x: f"${x:+,.0f}"),
        textposition="outside"
    ))
    fig_month.update_layout(
        height=260, margin=dict(l=0,r=0,t=20,b=0),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(gridcolor="rgba(128,128,128,0.1)"),
        xaxis=dict(gridcolor="rgba(0,0,0,0)"),
        showlegend=False
    )
    st.plotly_chart(fig_month, use_container_width=True)

    st.dataframe(
        monthly[["month","pnl","trades","wins","win_rate"]].rename(
            columns={"month":"Mes","pnl":"P&L","trades":"Trades","wins":"Ganadoras","win_rate":"Win Rate %"}
        ).style.format({"P&L":"${:+,.2f}","Win Rate %":"{:.1f}%"}),
        use_container_width=True, hide_index=True
    )

# ── Long vs Short ─────────────────────────────────────────────────────────────
st.subheader("Long vs Short")
by_side = df.groupby("side").agg(
    pnl=("pnl", "sum"),
    trades=("pnl", "count"),
    wins=("pnl", lambda x: (x > 0).sum())
).reset_index()
by_side["win_rate"] = (by_side["wins"] / by_side["trades"] * 100).round(1)
sc1, sc2 = st.columns(2)
for i, row in by_side.iterrows():
    col = sc1 if row["side"] == "long" else sc2
    icon = "🟢" if row["side"] == "long" else "🔴"
    col.metric(f"{icon} {row['side'].capitalize()} — P&L", f"${row['pnl']:,.2f}")
    col.metric(f"{icon} {row['side'].capitalize()} — Win Rate", f"{row['win_rate']:.1f}%")
    col.metric(f"{icon} {row['side'].capitalize()} — Trades", str(row['trades']))
