import streamlit as st
import pandas as pd

st.set_page_config(page_title="Notebook — Trading Journal", layout="wide", page_icon="📓")

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from db import init_db, get_notes, save_note, get_note
from styles import inject_css

init_db()
inject_css()

st.title("📓 Notebook de Trading")
st.caption("Registrá pensamientos, estrategias y aprendizajes de cada sesión.")

# ── Write new note ────────────────────────────────────────────────────────────
st.subheader("✍️ Nota del día")
col1, col2 = st.columns([1, 3])
with col1:
    note_date = st.date_input("Fecha", value=pd.Timestamp.today().date())
with col2:
    st.markdown("")

note_date_str = note_date.strftime("%Y-%m-%d")
existing = get_note(note_date_str)

note_content = st.text_area(
    "Escribí tu análisis, plan del día, emociones, aprendizajes...",
    value=existing,
    height=220,
    placeholder="¿Cómo estuvo el mercado hoy? ¿Seguiste tu plan? ¿Qué mejorarías?",
    key=f"nb_{note_date_str}"
)

if st.button("💾 Guardar nota", type="primary"):
    save_note(note_date_str, note_content)
    st.success("Nota guardada.")
    st.rerun()

# ── All notes list ────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("📚 Notas anteriores")

all_notes = get_notes()
if all_notes.empty:
    st.info("Aún no hay notas guardadas.")
else:
    search = st.text_input("🔍 Buscar en notas", placeholder="Palabra clave...")
    
    filtered_notes = all_notes.copy()
    if search:
        filtered_notes = filtered_notes[
            filtered_notes["content"].str.contains(search, case=False, na=False) |
            filtered_notes["date"].str.contains(search, na=False)
        ]
    
    st.caption(f"{len(filtered_notes)} nota(s)")

    for _, row in filtered_notes.iterrows():
        date_dt = pd.to_datetime(row["date"])
        date_label = date_dt.strftime("%A %d de %B, %Y").capitalize()
        content_preview = str(row["content"] or "")[:120] + ("..." if len(str(row["content"] or "")) > 120 else "")
        
        with st.expander(f"📅 {date_label} — {content_preview}", expanded=False):
            st.markdown(row["content"] or "*Sin contenido*")
            
            edit_key = f"edit_{row['date']}"
            if st.button("✏️ Editar esta nota", key=edit_key):
                st.session_state[f"editing_{row['date']}"] = True
                st.rerun()
            
            if st.session_state.get(f"editing_{row['date']}", False):
                new_content = st.text_area(
                    "Editar nota", value=row["content"] or "", height=160,
                    key=f"edit_area_{row['date']}"
                )
                if st.button("Guardar cambios", key=f"save_edit_{row['date']}", type="primary"):
                    save_note(row["date"], new_content)
                    st.session_state[f"editing_{row['date']}"] = False
                    st.success("Nota actualizada.")
                    st.rerun()
