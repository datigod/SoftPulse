import streamlit as st
import pandas as pd
import random
from statsmodels.tsa.holtwinters import SimpleExpSmoothing
import matplotlib.pyplot as plt

# Título
st.title("🌸 Pipeline Económico Jalmeidístico para la Producción de Flores")

# Sidebar - Parámetros modificables
st.sidebar.header("⚙️ Parámetros de Configuración")
operarios_cosecha = st.sidebar.slider("Operarios Cosecha", 5, 30, 10)
operarios_postcosecha = st.sidebar.slider("Operarios Postcosecha", 5, 30, 10)
horas_regulares = st.sidebar.slider("Horas Regulares por Operario", 100, 200, 160)
horas_extra = st.sidebar.slider("Horas Extra por Operario", 0, 80, 40)
costo_hora_regular = st.sidebar.slider("Costo Hora Regular ($)", 10, 50, 20)
costo_hora_extra = st.sidebar.slider("Costo Hora Extra ($)", 20, 70, 30)
usar_pronostico = st.sidebar.checkbox("Usar Pronóstico", True)

# Datos base
meses = ['ene-25', 'feb-25', 'mar-25', 'abr-25', 'may-25', 'jun-25',
         'jul-25', 'ago-25', 'sep-25', 'oct-25', 'nov-25', 'dic-25']
demanda_cosecha_real = [6, 9, 6, 7, 11, 6, 7, 7, 7, 6, 7, 7]
demanda_postcosecha_real = [432, 636, 399, 468, 754, 389, 469, 449, 470, 426, 482, 517]

# Pronóstico
if usar_pronostico:
    modelo_post = SimpleExpSmoothing(demanda_postcosecha_real).fit(smoothing_level=0.6)
    demanda_postcosecha = modelo_post.forecast(12).round(0).tolist()
    modelo_cosecha = SimpleExpSmoothing(demanda_cosecha_real).fit(smoothing_level=0.6)
    demanda_cosecha = modelo_cosecha.forecast(12).round(0).tolist()
else:
    demanda_cosecha = demanda_cosecha_real
    demanda_postcosecha = demanda_postcosecha_real

# Capacidad total
capacidad_total_cosecha = operarios_cosecha * (horas_regulares + horas_extra)
capacidad_total_postcosecha = operarios_postcosecha * (horas_regulares + horas_extra)

# Funciones para tiempos aleatorios
def tiempo_corte_flor():
    return random.uniform(2, 3) / 3600

def tiempo_hidratacion():
    return random.uniform(1, 2)

def tiempo_clasificacion():
    return random.uniform(30, 45) / 60

def tiempo_empaque():
    return random.uniform(20, 30) / 60

# Generar reporte
reporte = []
total_regulares = 0
total_extras = 0
for i in range(12):
    horas_cosecha_reg = min(demanda_cosecha[i], operarios_cosecha * horas_regulares)
    horas_cosecha_ext = max(0, demanda_cosecha[i] - horas_cosecha_reg)

    horas_post_reg = min(demanda_postcosecha[i], operarios_postcosecha * horas_regulares)
    horas_post_ext = max(0, demanda_postcosecha[i] - horas_post_reg)

    total_horas_reg = horas_cosecha_reg + horas_post_reg
    total_horas_ext = horas_cosecha_ext + horas_post_ext

    costo_total_cosecha = horas_cosecha_reg * costo_hora_regular + horas_cosecha_ext * costo_hora_extra
    costo_total_post = horas_post_reg * costo_hora_regular + horas_post_ext * costo_hora_extra
    costo_total_mes = costo_total_cosecha + costo_total_post

    total_regulares += total_horas_reg * costo_hora_regular
    total_extras += total_horas_ext * costo_hora_extra

    estado_cosecha = "✅" if demanda_cosecha[i] <= capacidad_total_cosecha else f"❌ Faltan {demanda_cosecha[i] - capacidad_total_cosecha:.1f} H.H"
    estado_post = "✅" if demanda_postcosecha[i] <= capacidad_total_postcosecha else f"❌ Faltan {demanda_postcosecha[i] - capacidad_total_postcosecha:.1f} H.H"

    corte = tiempo_corte_flor()
    hidratacion = tiempo_hidratacion()
    clasificacion = tiempo_clasificacion()
    empaque = tiempo_empaque()

    reporte.append({
        "Mes": meses[i],
        "Demanda Cosecha (H.H)": demanda_cosecha[i],
        "Capacidad Cosecha": capacidad_total_cosecha,
        "Cosecha": estado_cosecha,
        "Demanda Postcosecha (H.H)": demanda_postcosecha[i],
        "Capacidad Postcosecha": capacidad_total_postcosecha,
        "Postcosecha": estado_post,
        "Costo Cosecha ($)": round(costo_total_cosecha, 2),
        "Costo Postcosecha ($)": round(costo_total_post, 2),
        "Costo Total Mes ($)": round(costo_total_mes, 2),
        "T. Corte (h)": round(corte * 12, 4),
        "T. Hidratación (h)": round(hidratacion, 4),
        "T. Clasificación (h)": round(clasificacion, 4),
        "T. Empaque (h)": round(empaque, 4)
    })

df = pd.DataFrame(reporte)

# Mostrar métricas económicas agregadas
st.subheader("💰 Costos Acumulados del Año")
col1, col2 = st.columns(2)
col1.metric("Costo Total Horas Regulares ($)", f"{round(total_regulares, 2):,}")
col2.metric("Costo Total Horas Extra ($)", f"{round(total_extras, 2):,}")

# Mostrar tabla
st.subheader("📋 Resultados Mensuales")
st.dataframe(df)

# Gráfico de costos
st.subheader("📊 Costos Totales por Mes")
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(df["Mes"], df["Costo Total Mes ($)"], marker='o', label="Costo Total")
ax.bar(df["Mes"], df["Costo Cosecha ($)"], alpha=0.6, label="Cosecha")
ax.bar(df["Mes"], df["Costo Postcosecha ($)"], alpha=0.6, label="Postcosecha", bottom=df["Costo Cosecha ($)"])
ax.set_ylabel("Costo ($)")
ax.set_xlabel("Mes")
ax.set_title("Costo Total de Operación Mensual")
ax.legend()
ax.grid(True)
plt.xticks(rotation=45)
st.pyplot(fig)
