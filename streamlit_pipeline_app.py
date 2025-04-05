import streamlit as st
import pandas as pd
import random
from statsmodels.tsa.holtwinters import SimpleExpSmoothing
import matplotlib.pyplot as plt

# Título
st.title("🌸 Pipeline Jalmeidístico de Planeación de Flores")

# Inputs del usuario
st.sidebar.header("⚙️ Parámetros del Sistema")
operarios_cosecha = st.sidebar.slider("Operarios en Cosecha", 5, 30, 10)
operarios_postcosecha = st.sidebar.slider("Operarios en Postcosecha", 5, 30, 10)
horas_regulares = st.sidebar.slider("Horas Regulares por Operario", 100, 200, 160)
horas_extra = st.sidebar.slider("Horas Extra por Operario", 0, 80, 40)
usar_pronostico = st.sidebar.checkbox("Usar Pronóstico", True)

# Meses y demanda histórica
meses = ['ene-25', 'feb-25', 'mar-25', 'abr-25', 'may-25', 'jun-25',
         'jul-25', 'ago-25', 'sep-25', 'oct-25', 'nov-25', 'dic-25']
demanda_cosecha_real = [6, 9, 6, 7, 11, 6, 7, 7, 7, 6, 7, 7]
demanda_postcosecha_real = [432, 636, 399, 468, 754, 389, 469, 449, 470, 426, 482, 517]

# Pronóstico (si se usa)
if usar_pronostico:
    modelo_post = SimpleExpSmoothing(demanda_postcosecha_real).fit(smoothing_level=0.6)
    demanda_postcosecha = modelo_post.forecast(12).round(0).tolist()
    modelo_cosecha = SimpleExpSmoothing(demanda_cosecha_real).fit(smoothing_level=0.6)
    demanda_cosecha = modelo_cosecha.forecast(12).round(0).tolist()
else:
    demanda_cosecha = demanda_cosecha_real
    demanda_postcosecha = demanda_postcosecha_real

# Capacidad
capacidad_total_cosecha = operarios_cosecha * (horas_regulares + horas_extra)
capacidad_total_postcosecha = operarios_postcosecha * (horas_regulares + horas_extra)

# Funciones de simulación de sensores
def tiempo_corte_flor():
    return random.uniform(2, 3) / 3600

def tiempo_hidratacion():
    return random.uniform(1, 2)

def tiempo_clasificacion():
    return random.uniform(30, 45) / 60

def tiempo_empaque():
    return random.uniform(20, 30) / 60

# Reporte
reporte = []
for i in range(12):
    falta_cosecha = demanda_cosecha[i] - capacidad_total_cosecha
    falta_post = demanda_postcosecha[i] - capacidad_total_postcosecha

    estado_cosecha = "✅ Suficiente" if falta_cosecha <= 0 else f"❌ Faltan {falta_cosecha:.1f} H.H"
    estado_post = "✅ Suficiente" if falta_post <= 0 else f"❌ Faltan {falta_post:.1f} H.H"

    corte = tiempo_corte_flor()
    hidratacion = tiempo_hidratacion()
    clasificacion = tiempo_clasificacion()
    empaque = tiempo_empaque()
    tiempo_post_total = hidratacion + clasificacion + empaque

    reporte.append({
        "Mes": meses[i],
        "Demanda Cosecha (H.H)": demanda_cosecha[i],
        "Capacidad Cosecha (H.H)": capacidad_total_cosecha,
        "Resultado Cosecha": estado_cosecha,
        "Demanda Postcosecha (H.H)": demanda_postcosecha[i],
        "Capacidad Postcosecha (H.H)": capacidad_total_postcosecha,
        "Resultado Postcosecha": estado_post,
        "T. Corte (h)": round(corte * 12, 4),
        "T. Hidratación (h)": round(hidratacion, 4),
        "T. Clasificación (h)": round(clasificacion, 4),
        "T. Empaque (h)": round(empaque, 4),
        "T. Total Postcosecha (h)": round(tiempo_post_total, 4)
    })

df = pd.DataFrame(reporte)
st.dataframe(df)

# Gráficos
fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

# Cosecha
axes[0].bar(meses, df["Demanda Cosecha (H.H)"], label="Demanda Cosecha", color='skyblue')
axes[0].plot(meses, df["Capacidad Cosecha (H.H)"], label="Capacidad Cosecha", color='green', linestyle='--', marker='o')
axes[0].set_title("Cosecha: Demanda vs Capacidad")
axes[0].legend()
axes[0].grid(True)

# Postcosecha
axes[1].bar(meses, df["Demanda Postcosecha (H.H)"], label="Demanda Postcosecha", color='orange')
axes[1].plot(meses, df["Capacidad Postcosecha (H.H)"], label="Capacidad Postcosecha", color='green', linestyle='--', marker='o')
axes[1].set_title("Postcosecha: Demanda vs Capacidad")
axes[1].legend()
axes[1].grid(True)

plt.xticks(rotation=45)
plt.tight_layout()
st.pyplot(fig)
