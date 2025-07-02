# --- IMPORTACIONES ---
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import re
from streamlit_lottie import st_lottie  # type: ignore
import requests
import joblib
from xhtml2pdf import pisa  # type: ignore
import base64
import tempfile
import gc
# --- ESTILO DE FUENTE PERSONALIZADO ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Montserrat', sans-serif;
    }
    </style>
""", unsafe_allow_html=True)





# --- CONTRASEÑA DE ACCESO ---
PASSWORD = "fútbol2025"

# --- AUTENTICACIÓN ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.set_page_config(page_title="Informe Táctico", layout="centered")
    st.title("🔐 Ingreso seguro")
    pwd = st.text_input("Ingresá la contraseña para acceder a la app", type="password")

    if pwd == PASSWORD:
        st.session_state.authenticated = True
        st.success("Acceso concedido. ¡Bienvenido!")
        st.rerun()
    elif pwd:
        st.error("Contraseña incorrecta. Intentá de nuevo.")
        st.stop()

if not st.session_state.authenticated:
    st.stop()
  # --- LOGO EN APP AUTENTICADA (responsive para móviles) ---
st.markdown("""
    <style>
    .logo-app {
        position: fixed;
        top: 58px;
        left: 114px;
        z-index: 9999;
    }

    /* Ajustes para pantallas pequeñas */
    @media (max-width: 768px) {
        .logo-app {
            top: 20px;
            left: 20px;
        }
        .logo-app img {
            width: 80px;
        }
    }
    </style>
    <div class="logo-app">
        <img src="https://raw.githubusercontent.com/Martin-91400/app-tactica/main/Logo%201.png" width="115">
    </div>
""", unsafe_allow_html=True)













# --- CIERRE DE SESIÓN ---
if st.sidebar.button("🚪 Cerrar sesión"):
    st.session_state.authenticated = False
    st.rerun()

# --- ANIMACIÓN INICIAL ---
def cargar_lottie(url):
    r = requests.get(url)
    return r.json() if r.status_code == 200 else None

lottie_url = "https://assets10.lottiefiles.com/packages/lf20_49rdyysj.json"
animacion = cargar_lottie(lottie_url)
st_lottie(animacion, speed=1, width=700, height=300, loop=True)
st.title("⚽ Informe de Rendimiento del Rival")

# --- TÍTULO PRINCIPAL ---

# --- FUNCIÓN PARA VALIDAR NOMBRES ---
def es_nombre_valido(nombre):
    patron = r"^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s\-]{1,40}$"
    return re.match(patron, nombre)

# --- SECCIÓN 1: INFORME DEL RIVAL ---
st.warning("🔒 Los archivos no se guardan en el servidor. No incluyas datos personales sensibles.")
archivo_rival = st.file_uploader("📂 Subí archivo Excel del equipo rival", type="xlsx", key="rival")

if archivo_rival:
    try:
        df_rival = pd.read_excel(archivo_rival)
        jugadores = df_rival['Jugador'].dropna().unique().tolist()
        jugadores_validos = [j for j in jugadores if es_nombre_valido(j)]

        if not jugadores_validos:
            st.error("No hay nombres válidos.")
        else:
            seleccionado = st.selectbox("🎯 Elegí un jugador", jugadores_validos)
            st.subheader(f"📌 Detalle de {seleccionado}")
            st.write(df_rival[df_rival['Jugador'] == seleccionado])

            # --- Radar individual ---
            datos = df_rival[df_rival['Jugador'] == seleccionado].iloc[0]
            categorias = ['xG', 'Pases', 'Minutos', 'Intercepciones']
            valores = [datos[c] for c in categorias]
            maximos = [df_rival[c].max() for c in categorias]
            valores_norm = [v / m if m else 0 for v, m in zip(valores, maximos)]
            valores_norm += valores_norm[:1]
            angulos = np.linspace(0, 2 * np.pi, len(categorias), endpoint=False).tolist()
            angulos += angulos[:1]

            fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
            ax.plot(angulos, valores_norm, color='green')
            ax.fill(angulos, valores_norm, color='lime', alpha=0.4)
            ax.set_thetagrids(np.degrees(angulos[:-1]), categorias)
            ax.set_title(f"Radar de {seleccionado}")
            st.pyplot(fig)

        del df_rival, archivo_rival, datos, valores, maximos, valores_norm, angulos
        gc.collect()

    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")

# --- SECCIÓN 2: GRÁFICOS PERSONALIZADOS ---
st.header("📊 Gráficos personalizados")
archivo_grafico = st.file_uploader("📂 Subí CSV o Excel para graficar", type=["csv", "xlsx"], key="graficos")

if archivo_grafico:
    try:
        df = pd.read_csv(archivo_grafico) if archivo_grafico.name.endswith(".csv") else pd.read_excel(archivo_grafico)
        st.write("Vista previa:", df.head())

        columnas = df.select_dtypes(include='number').columns.tolist()
        seleccionadas = st.multiselect("Seleccioná columnas", columnas)
        tipo = st.selectbox("Tipo de gráfico", ["Barras", "Línea", "Radar"])

        if seleccionadas:
            if tipo == "Barras":
                st.bar_chart(df[seleccionadas])
            elif tipo == "Línea":
                st.line_chart(df[seleccionadas])
            elif tipo == "Radar" and len(seleccionadas) >= 3:
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
            st.info("Seleccioná al menos una columna para visualizar.")

        del df, archivo_grafico, columnas, seleccionadas
        gc.collect()

    except Exception as e:
        st.error(f"Error al graficar: {e}")
# --- SECCIÓN 3: EQUIPO PROPIO + PDF ---
st.header("📘 Informe del Equipo Propio")
archivo_propio = st.file_uploader("📂 Cargá archivo Excel del equipo propio", type="xlsx", key="propio")

if archivo_propio:
    try:
        df_propio = pd.read_excel(archivo_propio)
        jugadores_eq = df_propio['Jugador'].dropna().unique().tolist()
        jugadores_eq_validos = [j for j in jugadores_eq if es_nombre_valido(j)]

        if jugadores_eq_validos:
            seleccionado_eq = st.selectbox("🎽 Jugador del propio equipo", jugadores_eq_validos)
            datos_eq = df_propio[df_propio['Jugador'] == seleccionado_eq]
            st.subheader(f"📌 Detalle de {seleccionado_eq}")
            st.write(datos_eq)

            # --- Radar jugador propio ---
            datos_row = datos_eq.iloc[0]
            categorias_eq = ['xG', 'Pases', 'Minutos', 'Intercepciones']
            valores_eq = [datos_row[c] for c in categorias_eq]
            maximos_eq = [df_propio[c].max() for c in categorias_eq]
            valores_norm = [v / m if m else 0 for v, m in zip(valores_eq, maximos_eq)]
            valores_norm += valores_norm[:1]
            angulos_eq = np.linspace(0, 2 * np.pi, len(categorias_eq), endpoint=False).tolist()
            angulos_eq += angulos_eq[:1]

            fig_eq, ax_eq = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
            ax_eq.plot(angulos_eq, valores_norm, color='blue')
            ax_eq.fill(angulos_eq, valores_norm, color='skyblue', alpha=0.4)
            ax_eq.set_thetagrids(np.degrees(angulos_eq[:-1]), categorias_eq)
            ax_eq.set_title(f"Radar de {seleccionado_eq}")
            st.pyplot(fig_eq)

            # --- HTML para PDF ---
            html = f"""
            <html>
            <head><style>
            table {{border-collapse: collapse; width: 100%;}}
            th, td {{border: 1px solid #ccc; padding: 6px; text-align: center;}}
            body {{ font-family: Arial; font-size: 12px; }}
            </style></head>
            <body>
            <h2>Informe de {seleccionado_eq}</h2>
            {datos_eq.to_html(index=False)}
            <p><i>PDF generado automáticamente por la app de Martin</i></p>
            </body>
            </html>
            """

            def generar_pdf(html):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    pisa.CreatePDF(html, dest=tmp)
                    return tmp.name

            if st.button("📥 Generar PDF del Informe"):
                pdf_path = generar_pdf(html)
                with open(pdf_path, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode()
                    href = f'<a href="data:application/pdf;base64,{b64}" download="Informe_{seleccionado_eq}.pdf">📄 Descargar PDF</a>'
                    st.markdown(href, unsafe_allow_html=True)

        else:
            st.error("No hay jugadores válidos.")

    except Exception as e:
        st.error(f"Error al procesar el archivo del equipo propio: {e}")

    # Limpieza
    del df_propio, archivo_propio, jugadores_eq, jugadores_eq_validos, seleccionado_eq
    gc.collect()
# --- SECCIÓN 4: MODELO PREDICTIVO DE ESTILO Y COMPARATIVA ---
import plotly.graph_objects as go

st.header("🔮 Predicción y Comparativa de Estilo Táctico")

# Cargar modelo entrenado
try:
    modelo_estilo = joblib.load("modelo_estilo.pkl")
except FileNotFoundError:
    st.error("❌ No se encontró el archivo 'modelo_estilo.pkl'. Colocalo en la carpeta de la app.")
    st.stop()

col1, col2 = st.columns(2)

with col1:
    archivo_rival = st.file_uploader("📂 Subí datos del *equipo rival*", type=["csv", "xlsx"], key="modelo_rival")

with col2:
    archivo_propio = st.file_uploader("📂 Subí datos del *equipo propio*", type=["csv", "xlsx"], key="modelo_propio")

columnas_necesarias = ['Pases', 'Centros', 'Recuperaciones', 'Posesión', 'Altura']

if archivo_rival and archivo_propio:
    try:
        # Leer archivo rival con manejo de codificación
        if archivo_rival.name.endswith(".csv"):
            try:
                df_rival = pd.read_csv(archivo_rival, encoding='utf-8')
            except UnicodeDecodeError:
                df_rival = pd.read_csv(archivo_rival, encoding='latin-1')
        else:
            df_rival = pd.read_excel(archivo_rival)

        # Leer archivo propio con manejo de codificación
        if archivo_propio.name.endswith(".csv"):
            try:
                df_propio = pd.read_csv(archivo_propio, encoding='utf-8')
            except UnicodeDecodeError:
                df_propio = pd.read_csv(archivo_propio, encoding='latin-1')
        else:
            df_propio = pd.read_excel(archivo_propio)

    except Exception as e:
        st.error(f"🚨 Error al procesar los archivos: {e}")
        st.stop()


        