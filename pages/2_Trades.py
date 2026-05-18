import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Trades — Trading Journal", layout="wide", page_icon="📋")

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from db import init_db, get_all_trades, delete_trade
from styles import inject_css
from metrics import compute_metrics

init_db()
inject_css()

st.title("📋 Historial de Trades")

df = get_all_trades()

if df.empty:
    st.info("Aún no hay trades. Andá al **Calendario** para cargar tus primeras operaciones.")
    st.stop()

with st.expander("🔍 Filtros", expanded=False):
    fc1, fc2, fc3, fc4 = st.columns(4)
    symbols = ["Todos"] + sorted(df["symbol"].unique().tolist())
    sel_symbol = fc1.selectbox("Instrumento", symbols)
    sel_side = fc2.selectbox("Dirección", ["Todos", "Long", "Short"])
    sel_result = fc3.selectbox("Resultado", ["Todos", "Ganadoras", "Perdedoras"])
    if not df.empty:
        date_min = pd.to_datetime(df["date"]).min().date()
        date_max = pd.to_datetime(df["date"]).max().date()
        date_range = fc4.date_input("Rango de fechas", value=(date_min, date_max))
    else:
        date_range = None

filtered = df.copy()
filtered["date"] = pd.to_datetime(filtered["date"])

if sel_symbol != "Todos":
    filtered = filtered[filtered["symbol"] == sel_symbol]
if sel_side != "Todos":
    filtered = filtered[filtered["side"] == sel_side.lower()]
if sel_result == "Ganadoras":
    filtered = filtered[filtered["pnl"] > 0]
elif sel_result == "Perdedoras":
    filtered = filtered[filtered["pnl"] < 0]
if date_range and len(date_range) == 2:
    filtered = filtered[
        (filtered["date"].dt.date >= date_range[0]) &
        (filtered["date"].dt.date <= date_range[1])
    ]

st.markdown(f"**{len(filtered)} trades** con los filtros actuales")
m = compute_metrics(filtered)
mc1, mc2, mc3, mc4, mc5 = st.columns(5)
mc1.metric("P&L", f"${m['net_pnl']:,.2f}")
mc2.metric("Win Rate", f"{m['win_rate']:.1f}%")
mc3.metric("Profit Factor", f"{m['profit_factor']:.2f}" if m['profit_factor'] != float('inf') else "∞")
mc4.metric("Mejor trade", f"${m['best_trade']:,.2f}")
mc5.metric("Peor trade", f"${m['worst_trade']:,.2f}")

st.markdown("---")

display = filtered[["id","date","symbol","side","qty","entry","exit","pnl","note"]].copy()
display["date"] = display["date"].dt.strftime("%Y-%m-%d")
display["side"] = display["side"].map({"long": "🟢 Long", "short": "🔴 Short"})

def color_pnl(val):
    if isinstance(val, float) or isinstance(val, int):
        return f"color: {'#1D9E75' if val > 0 else '#D85A30' if val < 0 else 'inherit'}; font-weight: 500"
    return ""

styled = (
    display.rename(columns={"id":"ID","date":"Fecha","symbol":"Instrumento","side":"Dir",
                             "qty":"Contratos","entry":"Entrada","exit":"Salida","pnl":"P&L","note":"Nota"})
    .style.map(color_pnl, subset=["P&L"])
    .format({"P&L": "${:+.2f}", "Entrada": "{:.2f}", "Salida": "{:.2f}", "Contratos": "{:.0f}"})
)

st.dataframe(styled, use_container_width=True, hide_index=True)

st.markdown("---")
col_exp1, col_exp2 = st.columns([1, 4])
with col_exp1:
    csv_data = filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Exportar CSV",
        data=csv_data,
        file_name="trading_journal_trades.csv",
        mime="text/csv",
        use_container_width=True
    )

st.markdown("---")
st.markdown("#### 🗑 Eliminar trade por ID")
with st.form("delete_form", clear_on_submit=True):
    del_id = st.number_input("ID del trade a eliminar", min_value=1, step=1)
    if st.form_submit_button("Eliminar", type="secondary"):
        delete_trade(int(del_id))
        st.success(f"Trade #{del_id} eliminado.")
        st.rerun()
