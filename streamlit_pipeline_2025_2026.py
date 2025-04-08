import streamlit as st
import pandas as pd
import random
import matplotlib.pyplot as plt
from statsmodels.tsa.statespace.sarimax import SARIMAX

plt.style.use('dark_background')

st.set_page_config(layout="wide")
st.title("🌸 Pipeline - Proceso de Cosecha de Flores")

# SIDEBAR
st.sidebar.header("⚙️ Parámetros de Configuración")
operarios_cosecha = st.sidebar.slider("Operarios Cosecha", 1, 30, 10)
operarios_postcosecha = st.sidebar.slider("Operarios Postcosecha", 1, 30, 10)

st.sidebar.subheader("⏱️ Horas por Operario")
horas_regulares_cosecha = st.sidebar.number_input("Horas Regulares por Operario - Cosecha", 0, 200, 160)
horas_extra_cosecha = st.sidebar.number_input("Horas Extra por Operario - Cosecha", 0, 160, 80)
horas_regulares_post = st.sidebar.number_input("Horas Regulares por Operario - Postcosecha", 0, 200, 160)
horas_extra_post = st.sidebar.number_input("Horas Extra por Operario - Postcosecha", 0, 160, 80)

st.sidebar.subheader("💵 Costos")
costo_hora_regular = st.sidebar.slider("Costo Hora Regular ($)", 10, 50, 20)
costo_hora_extra = st.sidebar.slider("Costo Hora Extra ($)", 20, 70, 25)
costo_fijo_operario = 16  # Costo fijo mensual por operario

st.sidebar.subheader("🔧 Tiempos Estándar de los Procesos")
tiempo_corte_min = st.sidebar.number_input("Tiempo mínimo de Corte (segundos)", 1.0, 10.0, 2.0)
tiempo_corte_max = st.sidebar.number_input("Tiempo máximo de Corte (segundos)", 1.0, 10.0, 3.0)
tiempo_hidratacion_min = st.sidebar.number_input("Tiempo mínimo Hidratación (horas)", 0.5, 3.0, 1.0)
tiempo_hidratacion_max = st.sidebar.number_input("Tiempo máximo Hidratación (horas)", 0.5, 3.0, 2.0)
tiempo_clasificacion_min = st.sidebar.number_input("Tiempo mínimo Clasificación (minutos)", 10.0, 60.0, 30.0)
tiempo_clasificacion_max = st.sidebar.number_input("Tiempo máximo Clasificación (minutos)", 10.0, 60.0, 45.0)
tiempo_empaque_min = st.sidebar.number_input("Tiempo mínimo Empaque (minutos)", 5.0, 60.0, 20.0)
tiempo_empaque_max = st.sidebar.number_input("Tiempo máximo Empaque (minutos)", 5.0, 60.0, 30.0)

usar_pronostico = st.sidebar.checkbox("Usar SARIMAX desde enero 2026", False)

# DATOS
meses_2025 = ['ene-25', 'feb-25', 'mar-25', 'abr-25', 'may-25', 'jun-25',
              'jul-25', 'ago-25', 'sep-25', 'oct-25', 'nov-25', 'dic-25']
demanda_cosecha_real = [6, 9, 6, 7, 11, 6, 7, 7, 7, 6, 7, 7]
demanda_postcosecha_real = [432, 636, 399, 468, 754, 389, 469, 449, 470, 426, 482, 517]

# PRONÓSTICO
if usar_pronostico:
    modelo_cosecha = SARIMAX(demanda_cosecha_real, order=(1, 1, 1)).fit(disp=False)
    forecast_cosecha = modelo_cosecha.forecast(steps=12).round().tolist()

    modelo_post = SARIMAX(demanda_postcosecha_real, order=(1, 1, 1)).fit(disp=False)
    forecast_post = modelo_post.forecast(steps=12).round().tolist()

    meses = ['ene-26', 'feb-26', 'mar-26', 'abr-26', 'may-26', 'jun-26',
             'jul-26', 'ago-26', 'sep-26', 'oct-26', 'nov-26', 'dic-26']
    demanda_cosecha = forecast_cosecha
    demanda_postcosecha = forecast_post
else:
    meses = meses_2025
    demanda_cosecha = demanda_cosecha_real
    demanda_postcosecha = demanda_postcosecha_real

# FUNCIONES RANDOM
def tiempo_corte_flor(): return random.uniform(tiempo_corte_min, tiempo_corte_max) / 3600
def tiempo_hidratacion(): return random.uniform(tiempo_hidratacion_min, tiempo_hidratacion_max)
def tiempo_clasificacion(): return random.uniform(tiempo_clasificacion_min, tiempo_clasificacion_max) / 60
def tiempo_empaque(): return random.uniform(tiempo_empaque_min, tiempo_empaque_max) / 60

# SIMULACIÓN
reporte = []
total_regulares = 0
total_extras = 0
total_fijos = 0

for i in range(12):
    capacidad_reg_cosecha = operarios_cosecha * horas_regulares_cosecha
    capacidad_ext_cosecha = operarios_cosecha * horas_extra_cosecha
    capacidad_reg_post = operarios_postcosecha * horas_regulares_post
    capacidad_ext_post = operarios_postcosecha * horas_extra_post

    demanda_c = demanda_cosecha[i]
    demanda_p = demanda_postcosecha[i]

    horas_cosecha_reg = min(demanda_c, capacidad_reg_cosecha)
    horas_cosecha_ext = min(max(0, demanda_c - horas_cosecha_reg), capacidad_ext_cosecha)
    horas_post_reg = min(demanda_p, capacidad_reg_post)
    horas_post_ext = min(max(0, demanda_p - horas_post_reg), capacidad_ext_post)

    costo_total_cosecha = horas_cosecha_reg * costo_hora_regular + horas_cosecha_ext * costo_hora_extra
    costo_total_post = horas_post_reg * costo_hora_regular + horas_post_ext * costo_hora_extra
    costo_total_mes = costo_total_cosecha + costo_total_post

    costo_fijo_mes = (operarios_cosecha + operarios_postcosecha) * costo_fijo_operario
    total_fijos += costo_fijo_mes
    total_regulares += horas_cosecha_reg * costo_hora_regular + horas_post_reg * costo_hora_regular
    total_extras += horas_cosecha_ext * costo_hora_extra + horas_post_ext * costo_hora_extra

    estado_cosecha = "✅ Suficiente" if demanda_c <= (capacidad_reg_cosecha + capacidad_ext_cosecha) else "❌ Insuficiente"
    estado_post = "✅ Suficiente" if demanda_p <= (capacidad_reg_post + capacidad_ext_post) else "❌ Insuficiente"

    corte = tiempo_corte_flor()
    hidratacion = tiempo_hidratacion()
    clasificacion = tiempo_clasificacion()
    empaque = tiempo_empaque()

    reporte.append({
        "Mes": meses[i],
        "Demanda Cosecha (H.H)": demanda_c,
        "Capacidad Cosecha": capacidad_reg_cosecha + capacidad_ext_cosecha,
        "Resultado Cosecha": estado_cosecha,
        "Demanda Postcosecha (H.H)": demanda_p,
        "Capacidad Postcosecha": capacidad_reg_post + capacidad_ext_post,
        "Resultado Postcosecha": estado_post,
        "Costo Cosecha ($)": round(costo_total_cosecha, 2),
        "Costo Postcosecha ($)": round(costo_total_post, 2),
        "Costo Total Mes ($)": round(costo_total_mes + costo_fijo_mes, 2),
        "T. Corte (h)": round(corte * 12, 4),
        "T. Hidratación (h)": round(hidratacion, 4),
        "T. Clasificación (h)": round(clasificacion, 4),
        "T. Empaque (h)": round(empaque, 4)
    })

df = pd.DataFrame(reporte)

# VISUALIZACIONES
st.subheader("💰 Costos Anuales Acumulados")
col1, col2, col3, col4 = st.columns(4)
col1.metric("💼 Costo Total Horas Regulares", f"${round(total_regulares, 2):,}")
col2.metric("🕒 Costo Total Horas Extra", f"${round(total_extras, 2):,}")
col3.metric("📦 Costo Fijo por Operarios", f"${round(total_fijos, 2):,}")
col4.metric("🧾 Costo Total", f"${round(total_regulares + total_extras + total_fijos, 2):,}")

st.subheader("📋 Reporte Mensual de Simulación")
st.dataframe(df, use_container_width=True)

# GRAFICAS
st.subheader("📊 Capacidad vs Demanda")

fig1, ax1 = plt.subplots(figsize=(10, 4))
ax1.bar(df['Mes'], df['Demanda Cosecha (H.H)'], label='Demanda Cosecha', color='#EF476F')
ax1.plot(df['Mes'], df['Capacidad Cosecha'], label='Capacidad Cosecha', color='#FFD166', marker='o', linestyle='--')
ax1.set_title("Cosecha: Demanda vs Capacidad")
ax1.legend()
st.pyplot(fig1)

fig2, ax2 = plt.subplots(figsize=(10, 4))
ax2.bar(df['Mes'], df['Demanda Postcosecha (H.H)'], label='Demanda Postcosecha', color='#06D6A0')
ax2.plot(df['Mes'], df['Capacidad Postcosecha'], label='Capacidad Postcosecha', color='#118AB2', marker='o', linestyle='--')
ax2.set_title("Postcosecha: Demanda vs Capacidad")
ax2.legend()
st.pyplot(fig2)

fig3, ax3 = plt.subplots(figsize=(10, 4))
ax3.plot(df['Mes'], df['Costo Total Mes ($)'], marker='o', linestyle='-', color='#FFD166', label='Costo Total Mensual')
ax3.set_title("Costo Total Mensual ($)")
ax3.set_ylabel("USD")
ax3.grid(True)
ax3.legend()
st.pyplot(fig3)
