import streamlit as st
import pandas as pd
import random
import matplotlib.pyplot as plt
from statsmodels.tsa.statespace.sarimax import SARIMAX
from datetime import datetime
from dateutil.relativedelta import relativedelta

# Configuración de página
st.set_page_config(layout="wide", page_title="Gemelo Digital - Pipeline de Producción de Flores")

# Título principal
st.title("🌸 Pipeline Jalmeidístico con Pronóstico y Métricas de Producción (2025-2026)")

# Parámetros modificables
st.sidebar.header("⚙️ Configuración de Operarios")
operarios_cosecha = st.sidebar.slider("Operarios Cosecha", 5, 30, 10)
operarios_postcosecha = st.sidebar.slider("Operarios Postcosecha", 5, 30, 10)
horas_regulares = st.sidebar.slider("Horas Regulares", 100, 200, 160)
horas_extra = st.sidebar.slider("Horas Extra", 0, 80, 40)

# Datos reales
demanda_cosecha_real = [6, 9, 6, 7, 11, 6, 7, 7, 7, 6, 7, 7]
demanda_postcosecha_real = [432, 636, 399, 468, 754, 389, 469, 449, 470, 426, 482, 517]
meses_reales = ['ene-25', 'feb-25', 'mar-25', 'abr-25', 'may-25', 'jun-25',
                'jul-25', 'ago-25', 'sep-25', 'oct-25', 'nov-25', 'dic-25']

# Pronóstico con SARIMAX
def pronosticar_serie(serie_real, pasos=12):
    serie = pd.Series(serie_real)
    modelo = SARIMAX(serie, order=(1,1,1), seasonal_order=(1,1,1,12), enforce_stationarity=False, enforce_invertibility=False)
    ajuste = modelo.fit(disp=False)
    return ajuste.forecast(steps=pasos).round().tolist()

demanda_cosecha_forecast = pronosticar_serie(demanda_cosecha_real)
demanda_postcosecha_forecast = pronosticar_serie(demanda_postcosecha_real)

# Concatenar series
start_date = datetime.strptime("2026-01", "%Y-%m")
meses_forecast = [(start_date + relativedelta(months=i)).strftime("%b-%y") for i in range(12)]
meses_total = meses_reales + meses_forecast
demanda_cosecha_total = demanda_cosecha_real + demanda_cosecha_forecast
demanda_postcosecha_total = demanda_postcosecha_real + demanda_postcosecha_forecast

# Simulación de sensores
def tiempo_corte_flor(): return random.uniform(2, 3) / 3600
def tiempo_hidratacion(): return random.uniform(1, 2)
def tiempo_clasificacion(): return random.uniform(30, 45) / 60
def tiempo_empaque(): return random.uniform(20, 30) / 60

# Cálculo de capacidades
capacidad_total_cosecha = operarios_cosecha * (horas_regulares + horas_extra)
capacidad_total_postcosecha = operarios_postcosecha * (horas_regulares + horas_extra)

# Generación del reporte completo
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

# Mostrar tabla
st.subheader("📋 Resumen Completo (2025 y Pronóstico 2026)")
st.dataframe(df, use_container_width=True)

# Gráfico
fig, ax = plt.subplots(2, 1, figsize=(14, 8), sharex=True, facecolor="#0e1117")
fig.patch.set_facecolor('#0e1117')

# Gráfico de Cosecha
ax[0].bar(meses_total, df["Demanda Cosecha (H.H)"], color='deepskyblue', label="Demanda Cosecha")
ax[0].plot(meses_total, df["Capacidad Cosecha (H.H)"], color='lime', linestyle='--', marker='o', label="Capacidad")
ax[0].set_title("Cosecha - Demanda vs Capacidad", color="white")
ax[0].legend()
ax[0].tick_params(axis='x', rotation=45, labelcolor='white')
ax[0].tick_params(axis='y', labelcolor='white')
ax[0].set_facecolor('#0e1117')

# Gráfico de Postcosecha
ax[1].bar(meses_total, df["Demanda Postcosecha (H.H)"], color='orange', label="Demanda Postcosecha")
ax[1].plot(meses_total, df["Capacidad Postcosecha (H.H)"], color='lime', linestyle='--', marker='o', label="Capacidad")
ax[1].set_title("Postcosecha - Demanda vs Capacidad", color="white")
ax[1].legend()
ax[1].tick_params(axis='x', rotation=45, labelcolor='white')
ax[1].tick_params(axis='y', labelcolor='white')
ax[1].set_facecolor('#0e1117')

st.pyplot(fig)
