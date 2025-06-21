import streamlit as st
st.image("logo.png", width=150)

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

st.title("📊 Informe de Rendimiento del Rival")
st.write("Subí una planilla Excel con los datos del equipo rival (xG, pases, intercepciones, etc).")

archivo = st.file_uploader("📂 Cargar archivo Excel", type="xlsx")

if archivo:
    df = pd.read_excel(archivo)

    jugadores = df['Jugador'].unique()
    seleccionado = st.selectbox("🎯 Elegí un jugador", jugadores)

    st.subheader(f"📌 Detalle de {seleccionado}")
    st.write(df[df['Jugador'] == seleccionado])

    # 📈 RADAR DE RENDIMIENTO
    datos = df[df['Jugador'] == seleccionado].iloc[0]
    categorias = ['xG', 'Pases', 'Minutos', 'Intercepciones']
    valores = [datos[c] for c in categorias]
    maximos = [df[c].max() for c in categorias]
    valores_norm = [v / m if m != 0 else 0 for v, m in zip(valores, maximos)]

    etiquetas = categorias
    num_vars = len(etiquetas)
    valores_norm += valores_norm[:1]
    angulos = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angulos += angulos[:1]

    fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
    ax.plot(angulos, valores_norm, color='blue', linewidth=2)
    ax.fill(angulos, valores_norm, color='skyblue', alpha=0.4)
    ax.set_thetagrids(np.degrees(angulos[:-1]), etiquetas)
    ax.set_title(f"Radar de {seleccionado}", size=14)
    st.pyplot(fig)

else:
    st.info("Esperando archivo... podés usar una planilla con columnas como 'Jugador', 'xG', 'Pases', etc.")

