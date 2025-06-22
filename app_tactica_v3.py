import streamlit as st
from streamlit_lottie import st_lottie
import pandas as pd
import plotly.express as px
import requests

# Función para cargar animaciones Lottie
def cargar_lottie(url):
    r = requests.get(url)
    if r.status_code == 200:
        return r.json()
    return None

# Configuración de la página
st.set_page_config(page_title="Informe Táctico", layout="wide")
st.title("📊 Informe de Rendimiento del Rival")

# Animación 1: Introducción con gráfico dinámico
lottie_url_1 = "https://assets2.lottiefiles.com/packages/lf20_lrrvuhwz.json"
animacion_1 = cargar_lottie(lottie_url_1)
if animacion_1:
    st_lottie(animacion_1, height=240, key="intro_1")
else:
    st.warning("⚠️ No se pudo cargar la animación 1.")

# Separador
st.markdown("---")

# Animación 2: Acción táctica deportiva
lottie_url_2 = "https://assets7.lottiefiles.com/packages/lf20_1pxqjqps.json"
animacion_2 = cargar_lottie(lottie_url_2)
if animacion_2:
    st_lottie(animacion_2, height=240, key="intro_2")
else:
    st.warning("⚠️ No se pudo cargar la animación 2.")

# Cargar archivo Excel
archivo = st.file_uploader("📁 Subí el archivo Excel con los datos del rival", type=["xlsx"])
if archivo is not None:
    df = pd.read_excel(archivo)

    st.subheader("📋 Vista previa de los datos")
    st.dataframe(df)

    # Gráfico de radar si hay columnas adecuadas
    if 'Jugador' in df.columns:
        columnas_numericas = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
        opciones = st.multiselect("Seleccioná hasta 6 estadísticas para comparar", columnas_numericas, max_selections=6)

        if len(opciones) > 1:
            jugador_seleccionado = st.selectbox("Seleccioná un jugador", df['Jugador'].unique())
            datos_jugador = df[df['Jugador'] == jugador_seleccionado][opciones].values.flatten().tolist()

            df_radar = pd.DataFrame(dict(
                r=datos_jugador + [datos_jugador[0]],
                theta=opciones + [opciones[0]]
            ))

            st.subheader(f"📈 Radar de rendimiento: {jugador_seleccionado}")
            fig = px.line_polar(df_radar, r='r', theta='theta', line_close=True,
                                template="plotly_dark", line_shape="spline")
            fig.update_traces(fill='toself')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("⚠️ Seleccioná al menos 2 estadísticas para armar el radar.")
    else:
        st.error("❌ La tabla no contiene una columna llamada 'Jugador'.")







