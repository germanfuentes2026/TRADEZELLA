import streamlit as st
import pandas as pd
import calendar
from datetime import date, datetime
import io

st.set_page_config(page_title="Calendario — Trading Journal", layout="wide", page_icon="📅")

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from db import init_db, get_trades_by_date, get_daily_pnl, insert_trade, delete_trade, save_note, get_note, save_image, get_images_by_date, delete_image
from styles import inject_css
from metrics import compute_metrics

init_db()
inject_css()

# ── State ────────────────────────────────────────────────────────────────────
if "cal_year" not in st.session_state:
    st.session_state.cal_year = date.today().year
if "cal_month" not in st.session_state:
    st.session_state.cal_month = date.today().month
if "selected_date" not in st.session_state:
    st.session_state.selected_date = date.today().strftime("%Y-%m-%d")

MONTHS_ES = ["","Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]
DAYS_ES = ["Lun","Mar","Mié","Jue","Vie","Sáb","Dom"]

# ── Header ───────────────────────────────────────────────────────────────────
st.title("📅 Calendario de Trading")

col_prev, col_title, col_next = st.columns([1, 4, 1])
with col_prev:
    if st.button("◀  Mes anterior", use_container_width=True):
        if st.session_state.cal_month == 1:
            st.session_state.cal_month = 12
            st.session_state.cal_year -= 1
        else:
            st.session_state.cal_month -= 1
        st.rerun()

with col_title:
    st.markdown(
        f"<h2 style='text-align:center;margin:0;padding:8px 0'>"
        f"{MONTHS_ES[st.session_state.cal_month]} {st.session_state.cal_year}</h2>",
        unsafe_allow_html=True
    )

with col_next:
    if st.button("Mes siguiente  ▶", use_container_width=True):
        if st.session_state.cal_month == 12:
            st.session_state.cal_month = 1
            st.session_state.cal_year += 1
        else:
            st.session_state.cal_month += 1
        st.rerun()

# ── Monthly stats bar ────────────────────────────────────────────────────────
daily_pnl = get_daily_pnl()
year_str = str(st.session_state.cal_year)
month_str = str(st.session_state.cal_month).zfill(2)
month_prefix = f"{year_str}-{month_str}"

month_days = daily_pnl[daily_pnl["date"].str.startswith(month_prefix)] if not daily_pnl.empty else pd.DataFrame()
month_pnl = month_days["daily_pnl"].sum() if not month_days.empty else 0
month_trades = month_days["trade_count"].sum() if not month_days.empty else 0
month_green = (month_days["daily_pnl"] > 0).sum() if not month_days.empty else 0
month_red = (month_days["daily_pnl"] < 0).sum() if not month_days.empty else 0

ms1, ms2, ms3, ms4, ms5 = st.columns(5)
ms1.metric("P&L del mes", f"${month_pnl:,.2f}")
ms2.metric("Trades en el mes", str(int(month_trades)))
ms3.metric("Días positivos", str(int(month_green)))
ms4.metric("Días negativos", str(int(month_red)))
ms5.metric("Días operados", str(len(month_days)))

st.markdown("---")

# ── Calendar grid ────────────────────────────────────────────────────────────
# Build pnl lookup
pnl_lookup = {}
if not daily_pnl.empty:
    for _, row in daily_pnl.iterrows():
        pnl_lookup[row["date"]] = {"pnl": row["daily_pnl"], "count": row["trade_count"]}

cal = calendar.Calendar(firstweekday=0)  # Monday first
month_days_list = cal.monthdatescalendar(st.session_state.cal_year, st.session_state.cal_month)
today = date.today()

# Day headers
header_cols = st.columns(7)
for i, day_name in enumerate(DAYS_ES):
    header_cols[i].markdown(f"<div class='cal-header'>{day_name}</div>", unsafe_allow_html=True)

# Weeks
for week in month_days_list:
    cols = st.columns(7)
    for i, day in enumerate(week):
        with cols[i]:
            day_str = day.strftime("%Y-%m-%d")
            is_current_month = day.month == st.session_state.cal_month
            is_today = day == today
            is_selected = day_str == st.session_state.selected_date

            if not is_current_month:
                st.markdown("<div style='min-height:80px'></div>", unsafe_allow_html=True)
                continue

            day_data = pnl_lookup.get(day_str)
            has_trades = day_data is not None

            # Build cell style
            if is_selected:
                border = "2px solid #378ADD"
                bg = "#eff6ff"
            elif is_today:
                border = "2px solid #378ADD"
                bg = "#f0f7ff"
            elif has_trades and day_data["pnl"] >= 0:
                border = "1px solid rgba(29,158,117,0.4)"
                bg = "rgba(29,158,117,0.07)"
            elif has_trades and day_data["pnl"] < 0:
                border = "1px solid rgba(216,90,48,0.4)"
                bg = "rgba(216,90,48,0.07)"
            else:
                border = "1px solid #e2e5ef"
                bg = "#ffffff"

            pnl_html = ""
            if has_trades:
                p = day_data["pnl"]
                color = "#1D9E75" if p >= 0 else "#D85A30"
                sign = "+" if p >= 0 else ""
                pnl_html = f"""
                <div style='color:{color};font-weight:600;font-size:13px;margin-top:4px'>{sign}${p:,.0f}</div>
                <div style='font-size:10px;color:#9ca3af;margin-top:2px'>{int(day_data['count'])} trade{'s' if day_data['count']!=1 else ''}</div>
                """

            cell_html = f"""
            <div style='background:{bg};border:{border};border-radius:8px;padding:7px;min-height:78px;margin-bottom:2px'>
                <div style='font-size:11px;color:{"#378ADD" if is_today else "#9ca3af"};font-weight:{"600" if is_today else "500"}'>{day.day}</div>
                {pnl_html}
            </div>
            """
            st.markdown(cell_html, unsafe_allow_html=True)

            if st.button("Abrir", key=f"day_{day_str}", use_container_width=True, help=f"Ver {day_str}"):
                st.session_state.selected_date = day_str
                st.rerun()

# ── Selected day panel ───────────────────────────────────────────────────────
st.markdown("---")
sel = st.session_state.selected_date
sel_dt = datetime.strptime(sel, "%Y-%m-%d")
st.subheader(f"📌 {sel_dt.strftime('%A %d de %B de %Y').capitalize()}")

left_col, right_col = st.columns([3, 2])

with left_col:
    # ── Trades list ──────────────────────────────────────────────────────────
    st.markdown("#### Trades del día")
    trades_today = get_trades_by_date(sel)

    if trades_today.empty:
        st.info("Sin trades para este día.")
    else:
        day_metrics = compute_metrics(trades_today)
        dm1, dm2, dm3 = st.columns(3)
        dpnl = day_metrics["net_pnl"]
        dm1.metric("P&L", f"${dpnl:,.2f}")
        dm2.metric("Win Rate", f"{day_metrics['win_rate']:.0f}%")
        dm3.metric("Trades", str(day_metrics["total_trades"]))

        for _, row in trades_today.iterrows():
            p = float(row["pnl"])
            color = "#1D9E75" if p >= 0 else "#D85A30"
            side_label = "🟢 Long" if row["side"] == "long" else "🔴 Short"
            with st.expander(f"{row['symbol']} — {side_label} — ${p:+.2f}", expanded=False):
                ec1, ec2, ec3, ec4 = st.columns(4)
                ec1.write(f"**Contratos:** {row['qty']}")
                ec2.write(f"**Entrada:** {row['entry']}")
                ec3.write(f"**Salida:** {row['exit']}")
                ec4.write(f"**P&L:** ${p:+.2f}")
                if row["note"]:
                    st.markdown(f"📝 *{row['note']}*")
                if st.button("🗑 Eliminar trade", key=f"del_{row['id']}"):
                    delete_trade(int(row["id"]))
                    st.success("Trade eliminado.")
                    st.rerun()

    # ── Add trade form ───────────────────────────────────────────────────────
    st.markdown("#### ➕ Agregar trade")
    with st.form(key=f"add_trade_{sel}", clear_on_submit=True):
        f1, f2, f3 = st.columns(3)
        symbol = f1.text_input("Instrumento", placeholder="ES, NQ, CL, SPY...").upper()
        side = f2.selectbox("Dirección", ["long", "short"], format_func=lambda x: "🟢 Long" if x=="long" else "🔴 Short")
        qty = f3.number_input("Contratos", min_value=0.01, value=1.0, step=1.0)

        f4, f5, f6 = st.columns(3)
        entry = f4.number_input("Entrada", value=0.0, step=0.25, format="%.2f")
        exit_ = f5.number_input("Salida", value=0.0, step=0.25, format="%.2f")
        manual_pnl = f6.number_input("P&L directo ($)", value=0.0, step=0.01, format="%.2f",
                                      help="Si ingresás un valor aquí, se usa en vez del calculado.")

        note = st.text_input("Nota (setup, emoción, error...)", placeholder="Opcional")
        submitted = st.form_submit_button("Agregar trade ✅", use_container_width=True, type="primary")

        if submitted:
            if not symbol:
                st.error("Ingresá el instrumento.")
            else:
                if manual_pnl != 0.0:
                    pnl = manual_pnl
                elif entry != 0.0 and exit_ != 0.0:
                    pnl = (exit_ - entry) * qty if side == "long" else (entry - exit_) * qty
                else:
                    st.error("Ingresá el P&L o los precios de entrada y salida.")
                    st.stop()
                insert_trade(sel, symbol, side, qty, entry, exit_, round(pnl, 2), note)
                st.success(f"Trade {symbol} agregado — P&L: ${pnl:+.2f}")
                st.rerun()

with right_col:
    # ── Daily note ───────────────────────────────────────────────────────────
    st.markdown("#### 📓 Nota del día")
    current_note = get_note(sel)
    new_note = st.text_area("Escribí tu análisis, emociones, plan...", value=current_note, height=160, key=f"note_{sel}")
    if st.button("Guardar nota 💾", use_container_width=True):
        save_note(sel, new_note)
        st.success("Nota guardada.")

    # ── Chart images ─────────────────────────────────────────────────────────
    st.markdown("#### 📸 Gráficos del día")
    uploaded = st.file_uploader(
        "Subí capturas de tus setups", type=["png","jpg","jpeg","webp"],
        accept_multiple_files=True, key=f"upload_{sel}"
    )
    if uploaded:
        for f in uploaded:
            img_bytes = f.read()
            trade_id = None  # linked to day, not specific trade
            save_image(trade_id, sel, f.name, img_bytes)
        st.success(f"{len(uploaded)} imagen(es) guardada(s).")
        st.rerun()

    images = get_images_by_date(sel)
    if images:
        for img_id, trade_id, filename, data in images:
            with st.expander(f"📷 {filename}", expanded=True):
                st.image(data, use_container_width=True)
                if st.button("Eliminar imagen", key=f"delimg_{img_id}"):
                    delete_image(img_id)
                    st.rerun()
    else:
        st.caption("Sin gráficos para este día.")
