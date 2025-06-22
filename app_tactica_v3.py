import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import re
import streamlit.components.v1 as components

# Configuración de la página
st.set_page_config(page_title="Informe Táctico", layout="centered")
st.title("⚽ Informe de Rendimiento del Rival")

# Animación silenciosa embebida (sin texto)
video_code = '''
<video autoplay loop muted playsinline style="width:100%; height:300px; object-fit:contain;">
    <source src="Online_Statistics.mp4" type="video/mp4">
</video>
'''
components.html(video_code, height=300)

# Instrucción inicial
st.write("Subí una planilla Excel con los datos del equipo rival (xG, pases, intercepciones, etc).")

# Validación de nombres
def es_nombre_valido(nombre):
    patron = r"^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s\\-]{1,40}$"
    return re.match(patron, nombre)

def registrar_sospecha(valor):
    with open("log_segu.txt", "a") as log:
        log.write(f"Input sospechoso: {valor}\\n")

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

            # Radar individual del jugador
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
            ax.plot(angulos, valores_norm, color='green', linewidth=2)
            ax.fill(angulos, valores_norm, color='lime', alpha=0.4)
            ax.set_thetagrids(np.degrees(angulos[:-1]), etiquetas)
            ax.set_title(f"Radar de {seleccionado}", size=14)
            st.pyplot(fig)

    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")
else:
    st.info("Esperando que cargues la planilla del rival.")

# Sección 2: Creador de gráficos
st.header("📊 Creador de Gráficos Estadísticos")
archivo_grafico = st.file_uploader("📂 Subí tu archivo de datos (CSV o Excel)", type=["csv", "xlsx"], key="graficos")

if archivo_grafico:
    try:
        if archivo_grafico.name.endswith(".csv"):
            df = pd.read_csv(archivo_grafico)
        else:
            df = pd.read_excel(archivo_grafico)

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

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; font-size: 0.85em; color: gray;'>"
    "🛡️ App diseñada por <strong>Martin</strong> · Streamlit + Python · 2025"
    "</div>",
    unsafe_allow_html=True
)









