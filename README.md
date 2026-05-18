# 📈 Trading Journal — Futuros & Options

App de trading journal construida con Streamlit y SQLite. Tus datos se guardan localmente en `journal.db`.

---

## 🚀 Instalación local

### 1. Cloná o descomprimí la carpeta

```bash
cd trading_journal
```

### 2. Creá un entorno virtual (recomendado)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

### 3. Instalá las dependencias

```bash
pip install -r requirements.txt
```

### 4. Ejecutá la app

```bash
streamlit run app.py
```

Se abre automáticamente en `http://localhost:8501`

---

## ☁️ Deploy en Streamlit Cloud (gratis)

1. Subí la carpeta a un repositorio de **GitHub**
2. Andá a [share.streamlit.io](https://share.streamlit.io)
3. Conectá tu cuenta de GitHub
4. Seleccioná el repo y `app.py` como entry point
5. Click en **Deploy**

> ⚠️ En Streamlit Cloud el archivo `journal.db` se resetea al reiniciar el servidor. Para persistencia real en la nube, reemplazá SQLite por **Supabase** (PostgreSQL gratuito) o usá **st.session_state** para exportar/importar CSV.

---

## 📂 Estructura

```
trading_journal/
├── app.py                  # Dashboard principal
├── db.py                   # Base de datos SQLite
├── metrics.py              # Cálculo de estadísticas
├── styles.py               # CSS personalizado
├── requirements.txt
├── journal.db              # Se crea automáticamente
└── pages/
    ├── 1_Calendario.py     # Calendario + carga de trades + imágenes
    ├── 2_Trades.py         # Historial con filtros y exportación
    ├── 3_Estadisticas.py   # Gráficos y análisis completo
    └── 4_Notebook.py       # Notas diarias
```

---

## ✨ Funcionalidades

- 📅 **Calendario mensual** con días pintados en verde/rojo según P&L
- ➕ **Carga de trades**: instrumento, Long/Short, contratos, entrada/salida o P&L directo
- 📸 **Subida de gráficos** por día (PNG, JPG, WebP)
- 📓 **Nota diaria** por día de trading
- 📊 **Estadísticas**: Equity Curve, Win Rate, Profit Factor, Expectancy, Max Drawdown
- 📋 **Historial** con filtros por instrumento, dirección, resultado y fecha
- ⬇️ **Exportación a CSV**
- 🌙 Tema oscuro incluido
