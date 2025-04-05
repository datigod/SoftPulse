
import streamlit as st
import pandas as pd
import random
from statsmodels.tsa.statespace.sarimax import SARIMAX
import matplotlib.pyplot as plt
from dateutil.relativedelta import relativedelta
from datetime import datetime

st.set_page_config(layout="wide")
st.title("🌺 Gemelo Digital de Producción - Flores 2025-2026")

st.sidebar.header("⚙️ Parámetros del Sistema")
operarios_cosecha = st.sidebar.slider("Operarios en Cosecha", 5, 30, 10)
operarios_postcosecha = st.sidebar.slider("Operarios en Postcosecha", 5, 30, 10)
horas_regulares = st.sidebar.slider("Horas Regulares por Operario", 100, 200, 160)
horas_extra = st.sidebar.slider("Horas Extra por Operario", 0, 80, 40)

# Datos reales
demanda_cosecha_real = [6, 9, 6, 7, 11, 6, 7, 7, 7, 6, 7, 7]
demanda_postcosecha_real = [432, 636, 399, 468, 754, 389, 469, 449, 470, 426, 482, 517]
meses_reales = ['ene-25', 'feb-25', 'mar-25', 'abr-25', 'may-25', 'jun-25',
                'jul-25', 'ago-25', 'sep-25', 'oct-25', 'nov-25', 'dic-25']
start_date = datetime.strptime("2026-01", "%Y-%m")
meses_forecast = [(start_date + relativedelta(months=i)).strftime("%b-%y") for i in range(12)]

# Función de pronóstico robusto
def pronosticar_serie(serie_real, pasos=12):
    serie = pd.Series(serie_real)
    modelo = SARIMAX(serie, order=(1,1,1), seasonal_order=(1,1,1,12), enforce_stationarity=False, enforce_invertibility=False)
    ajuste = modelo.fit(disp=False)
    pred = ajuste.forecast(steps=pasos).round().tolist()
    return pred

# Generar demanda futura
demanda_cosecha = pronosticar_serie(demanda_cosecha_real)
demanda_postcosecha = pronosticar_serie(demanda_postcosecha_real)

# Concatenar todo
demanda_cosecha_total = demanda_cosecha_real + demanda_cosecha
demanda_postcosecha_total = demanda_postcosecha_real + demanda_postcosecha
meses_total = meses_reales + meses_forecast

# Capacidad total
capacidad_total_cosecha = operarios_cosecha * (horas_regulares + horas_extra)
capacidad_total_postcosecha = operarios_postcosecha * (horas_regulares + horas_extra)

# Simulación de sensores
def tiempo_corte_flor(): return random.uniform(2, 3) / 3600
def tiempo_hidratacion(): return random.uniform(1, 2)
def tiempo_clasificacion(): return random.uniform(30, 45) / 60
def tiempo_empaque(): return random.uniform(20, 30) / 60

# Generar reporte
reporte = []
for i in range(24):
    falta_cosecha = demanda_cosecha_total[i] - capacidad_total_cosecha
    falta_post = demanda_postcosecha_total[i] - capacidad_total_postcosecha

    estado_cosecha = "✅ Suficiente" if falta_cosecha <= 0 else f"❌ Faltan {falta_cosecha:.1f} H.H"
    estado_post = "✅ Suficiente" if falta_post <= 0 else f"❌ Faltan {falta_post:.1f} H.H"

    corte = tiempo_corte_flor()
    hidratacion = tiempo_hidratacion()
    clasificacion = tiempo_clasificacion()
    empaque = tiempo_empaque()
    tiempo_post_total = hidratacion + clasificacion + empaque

    takt_time_cosecha = capacidad_total_cosecha / demanda_cosecha_total[i] if demanda_cosecha_total[i] > 0 else None
    takt_time_post = capacidad_total_postcosecha / demanda_postcosecha_total[i] if demanda_postcosecha_total[i] > 0 else None
    wip_post = demanda_postcosecha_total[i] * tiempo_post_total

    reporte.append({
        "Mes": meses_total[i],
        "Demanda Cosecha (H.H)": demanda_cosecha_total[i],
        "Capacidad Cosecha (H.H)": capacidad_total_cosecha,
        "Resultado Cosecha": estado_cosecha,
        "Demanda Postcosecha (H.H)": demanda_postcosecha_total[i],
        "Capacidad Postcosecha (H.H)": capacidad_total_postcosecha,
        "Resultado Postcosecha": estado_post,
        "T. Corte (h)": round(corte * 12, 4),
        "T. Hidratación (h)": round(hidratacion, 4),
        "T. Clasificación (h)": round(clasificacion, 4),
        "T. Empaque (h)": round(empaque, 4),
        "Takt Time Cosecha": round(takt_time_cosecha, 2) if takt_time_cosecha else "-",
        "Takt Time Postcosecha": round(takt_time_post, 2) if takt_time_post else "-",
        "WIP Postcosecha (h)": round(wip_post, 2)
    })

df = pd.DataFrame(reporte)

# Mostrar tabla completa
st.subheader("📋 Reporte de Producción 2025 - 2026")
st.dataframe(df, use_container_width=True)

# Gráficas con fondo adaptado
fig, axes = plt.subplots(2, 1, figsize=(14, 8), sharex=True, facecolor='whitesmoke')
fig.patch.set_facecolor('whitesmoke')

axes[0].bar(df["Mes"], df["Demanda Cosecha (H.H)"], label="Demanda Cosecha", color='#91c2f3')
axes[0].plot(df["Mes"], df["Capacidad Cosecha (H.H)"], label="Capacidad Cosecha", color='green', linestyle='--', marker='o')
axes[0].set_title("Cosecha: Demanda vs Capacidad", fontsize=12)
axes[0].legend()
axes[0].grid(True)

axes[1].bar(df["Mes"], df["Demanda Postcosecha (H.H)"], label="Demanda Postcosecha", color='#f7a072')
axes[1].plot(df["Mes"], df["Capacidad Postcosecha (H.H)"], label="Capacidad Postcosecha", color='green', linestyle='--', marker='o')
axes[1].set_title("Postcosecha: Demanda vs Capacidad", fontsize=12)
axes[1].legend()
axes[1].grid(True)

plt.xticks(rotation=45)
plt.tight_layout()
st.pyplot(fig)
