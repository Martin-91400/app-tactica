# Tu código comienza acá
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import re
import streamlit.components.v1 as components
from streamlit_lottie import st_lottie
import requests
import pdfkit
import tempfile
import base64
import os

# --- Animación Lottie decorativa arriba del título ---
def cargar_lottie(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lottie_url = "https://assets10.lottiefiles.com/packages/lf20_49rdyysj.json"
animacion = cargar_lottie(lottie_url)
st_lottie(animacion, speed=1, width=700, height=300, loop=True)

# Configuración de página y título
st.set_page_config(page_title="Informe Táctico", layout="centered")
st.title("⚽ Informe de Rendimiento del Rival")
st.write("Subí una planilla Excel con los datos del equipo rival (xG, pases, intercepciones, etc).")

# Validación segura de nombres
def es_nombre_valido(nombre):
    patron = r"^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s\-]{1,40}$"
    return re.match(patron, nombre)

def registrar_sospecha(valor):
    with open("log_segu.txt", "a") as log:
        log.write(f"Input sospechoso: {valor}\n")

# Sección 1: Informe táctico
archivo_rival = st.file_uploader("📂 Cargar archivo Excel", type="xlsx", key="rival")
if archivo_rival:
    try:
        df_rival = pd.read_excel(archivo_rival)
        jugadores = df_rival['Jugador'].dropna().unique().tolist()
        jugadores_validos = [j for j in jugadores if es_nombre_valido(j)]

        if not jugadores_validos:
            st.error("Ningún nombre de jugador pasó la validación.")
        else:
            seleccionado = st.selectbox("🎯 Elegí un jugador", jugadores_validos)

            if not es_nombre_valido(seleccionado):
                st.warning("Nombre inválido.")
                registrar_sospecha(seleccionado)
                st.stop()

            st.subheader(f"📌 Detalle de {seleccionado}")
            st.write(df_rival[df_rival['Jugador'] == seleccionado])

            # Radar
            datos = df_rival[df_rival['Jugador'] == seleccionado].iloc[0]
            categorias = ['xG', 'Pases', 'Minutos', 'Intercepciones']
            valores = [datos[c] for c in categorias]
            maximos = [df_rival[c].max() for c in categorias]
            valores_norm = [v / m if m != 0 else 0 for v, m in zip(valores, maximos)]
            valores_norm += valores_norm[:1]
            angulos = np.linspace(0, 2 * np.pi, len(categorias), endpoint=False).tolist()
            angulos += angulos[:1]

            fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
            ax.plot(angulos, valores_norm, color='green', linewidth=2)
            ax.fill(angulos, valores_norm, color='lime', alpha=0.4)
            ax.set_thetagrids(np.degrees(angulos[:-1]), categorias)
            ax.set_title(f"Radar de {seleccionado}", size=14)
            st.pyplot(fig)
    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")
else:
    st.info("Esperando que cargues la planilla del rival.")

# Sección 2: Gráficos
st.header("📊 Creador de Gráficos Estadísticos")
archivo_grafico = st.file_uploader("📂 Subí tu archivo de datos (CSV o Excel)", type=["csv", "xlsx"], key="graficos")

if archivo_grafico:
    try:
        df = pd.read_csv(archivo_grafico) if archivo_grafico.name.endswith(".csv") else pd.read_excel(archivo_grafico)
        st.write("Vista previa:", df.head())
        columnas = df.select_dtypes(include='number').columns.tolist()
        seleccionadas = st.multiselect("Seleccioná columnas para graficar", columnas)
        tipo = st.selectbox("Tipo de gráfico", ["Barras", "Línea", "Radar"])

        if tipo == "Barras":
            st.bar_chart(df[seleccionadas])
        elif tipo == "Línea":
            st.line_chart(df[seleccionadas])
        elif tipo == "Radar":
            if len(seleccionadas) >= 3:
                fig = go.Figure()
                for i in range(len(df)):
                    fig.add_trace(go.Scatterpolar(
                        r=df.loc[i, seleccionadas].values,
                        theta=seleccionadas,
                        fill='toself',
                        name=f"Fila {i+1}"
                    ))
                fig.update_layout(polar=dict(radialaxis=dict(visible=True)))
                st.plotly_chart(fig)
            else:
                st.warning("Seleccioná al menos 3 columnas para radar.")
    except Exception as e:
        st.error(f"Error al procesar los datos: {e}")
else:
    st.info("Esperando archivo para generar gráficos.")

# Sección 3: Informe del Propio Equipo + PDF
st.header("📘 Informe del Propio Equipo")
archivo_propio = st.file_uploader("📂 Cargá los datos del equipo propio (Excel)", type="xlsx", key="propio")

if archivo_propio:
    try:
        df_propio = pd.read_excel(archivo_propio)
        jugadores_eq = df_propio['Jugador'].dropna().unique().tolist()
        jugadores_eq_validos = [j for j in jugadores_eq if es_nombre_valido(j)]

        if not jugadores_eq_validos:
            st.error("Ningún nombre válido en el archivo.")
        else:
            seleccionado_eq = st.selectbox("🎽 Elegí un jugador del propio equipo", jugadores_eq_validos)

            st.subheader(f"📌 Detalle de {seleccionado_eq}")
            datos_eq = df_propio[df_propio['Jugador'] == seleccionado_eq]
            st.write(datos_eq)

            # Radar propio
            datos_row = datos_eq.iloc[0]
            categorias_eq = ['xG', 'Pases', 'Minutos', 'Intercepciones']
            valores_eq = [datos_row[c] for c in categorias_eq]
            maximos_eq = [df_propio[c].max() for c in categorias_eq]
            valores_norm = [v / m if m != 0 else 0 for v, m in zip(valores_eq, maximos_eq)]
            valores_norm += valores_norm[:1]
            angulos_eq = np.linspace(0, 2 * np.pi, len(categorias_eq), endpoint=False).tolist()
            angulos_eq += angulos_eq[:1]

            fig_eq, ax_eq = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
            ax_eq.plot(angulos_eq, valores_norm, color='blue', linewidth=2)
            ax_eq.fill(angulos_eq, valores_norm, color='skyblue', alpha=0.4)
            ax_eq.set_thetagrids(np.degrees(angulos_eq[:-1]), categorias_eq)
            ax_eq.set_title(f"Radar de {seleccionado_eq}", size=14)
            st.pyplot(fig_eq)

            # Generar HTML para el PDF
            html_pdf = f"""
            <html>
            <head>
            <meta charset='utf-8'>
            <style>
                h2 {{ color: #2E86C1; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ border: 1px solid #ccc; padding: 6px; text-align: center; }}
                body {{ font-family: Arial; }}
            </style>
            </head>
            <body>
            <h2>Informe Individual – {seleccionado_eq}</h2>
            <p>Datos relevantes:</p>
            {datos_eq.to_html(index=False)}
            <p><i>Informe generado automáticamente por la app de Martin.</i></p>
            </body>
            </html>
            """

            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
                pdfkit.from_string(html_pdf, tmpfile.name)

            if os.path.exists(tmpfile.name):
                with open(tmpfile.name, "rb") as pdf_file:
                    b64 = base64.b64encode(pdf_file.read()).decode('utf-8')
                    st.subheader("⬇️ Exportar informe en PDF")












