import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import numpy as np
import re

st.set_page_config(page_title="Informe Táctico Seguro", layout="centered")
st.title("📊 Informe de Rendimiento del Rival (Versión Blindada)")

st.write("Subí una planilla Excel con los datos del equipo rival (xG, pases, intercepciones, etc).")

# Función de validación de input
def es_nombre_valido(nombre):
    patron = r"^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s\-]{1,40}$"
    return re.match(patron, nombre)

def registrar_sospecha(valor):
    with open("log_segu.txt", "a") as log:
        log.write(f"Input sospechoso: {valor}\n")

# 🚨 Sección 1: Informe táctico de jugador
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

            # 📈 Radar
            datos = df_rival[df_rival['Jugador'] == seleccionado].iloc[0]
            categorias = ['xG', 'Pases', 'Minutos', 'Intercepciones']
            valores = [datos[c] for c in categorias]
            maximos = [df_rival[c].max() for c in categorias]
            valores_norm = [v / m if m != 0 else 0 for v, m in zip(valores, maximos)]
            valores_norm += valores_norm[:1]
            etiquetas = categorias
            num_vars = len(etiquetas)
            angulos = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
            angulos += angulos[:1]

            fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
            ax.plot(angulos, valores_norm, color='blue', linewidth=2)
            ax.fill(angulos, valores_norm, color='skyblue', alpha=0.4)
            ax.set_thetagrids(np.degrees(angulos[:-1]), etiquetas)
            ax.set_title(f"Radar de {seleccionado}", size=14)
            st.pyplot(fig)
    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")
else:
    st.info("Esperando que cargues la planilla con datos del equipo rival.")

# 🚨 Sección 2: Gráficos estadísticos
st.header("📊 Creador de Gráficos Estadísticos")
archivo_grafico = st.file_uploader("📂 Subí tu archivo de datos (CSV o Excel)", type=["csv", "xlsx"], key="graficos")

if archivo_grafico:
    try:
        if archivo_grafico.name.endswith(".csv"):
            df = pd.read_csv(archivo_grafico)
        else:
            df = pd.read_excel(archivo_grafico)

        st.write("Vista previa de los datos:", df.head())

        columnas = df.select_dtypes(include='number').columns.tolist()
        seleccionadas = st.multiselect("Seleccioná las columnas para graficar", columnas)
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
                st.warning("Seleccioná al menos 3 columnas para gráfico radar.")
    except Exception as e:
        st.error(f"Error al procesar los datos: {e}")
else:
    st.info("Esperando que cargues un archivo con datos numéricos para los gráficos.")




