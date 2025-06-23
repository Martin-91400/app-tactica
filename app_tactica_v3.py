# --- IMPORTACIONES ---
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import re
from streamlit_lottie import st_lottie # type: ignore
import requests
from xhtml2pdf import pisa # type: ignore
import base64
import tempfile
import gc  # Garbage collector
# --- Autenticación segura ---
PASSWORD = "fútbol2025"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.set_page_config(page_title="Informe Táctico", layout="centered")
    st.title("🔐 Ingreso seguro")
    pwd = st.text_input("Ingresá la contraseña para acceder a la app", type="password", key="auth_pwd")

    if pwd == PASSWORD:
        st.session_state.authenticated = True
        st.success("Acceso concedido. ¡Bienvenido!")
        st.experimental_rerun()  # 🔁 Recarga para mostrar la app
    elif pwd:
        st.error("Contraseña incorrecta. Intentá de nuevo.")
        st.stop()





# --- ESTILOS VISUALES ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@600&family=Roboto&display=swap');

    html, body, [class*="css"] {
        font-family: 'Roboto', sans-serif;
        color: #2c3e50;
        font-size: 16px;
    }
    h1, h2, h3 {
        font-family: 'Montserrat', sans-serif;
        color: #1f618d;
    }
    .stButton>button {
        background-color: #117A65;
        color: white;
        border-radius: 6px;
        padding: 0.5em 1em;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #148F77;
        color: #f1f1f1;
    }
    a {
        color: #1F618D;
        text-decoration: none;
    }
    a:hover {
        text-decoration: underline;
    }
    table {
        border-collapse: collapse;
        width: 100%;
    }
    th, td {
        border: 1px solid #dcdcdc;
        padding: 6px;
        text-align: center;
    }
    th {
        background-color: #f2f2f2;
    }
    </style>
""", unsafe_allow_html=True)

# --- ANIMACIÓN INICIAL ---
def cargar_lottie(url):
    r = requests.get(url)
    return r.json() if r.status_code == 200 else None

lottie_url = "https://assets10.lottiefiles.com/packages/lf20_49rdyysj.json"
animacion = cargar_lottie(lottie_url)
st_lottie(animacion, speed=1, width=700, height=300, loop=True)

# --- TÍTULO PRINCIPAL ---
st.title("⚽ Informe de Rendimiento del Rival")


# --- BOTÓN: Cerrar sesión desde la barra lateral ---
if st.sidebar.button("🚪 Cerrar sesión"):
    st.session_state.authenticated = False
    st.experimental_rerun()


# --- FUNCIONES ÚTILES ---
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

            # Radar
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

            # Radar
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

        # Limpieza de datos
        del df_propio, archivo_propio, jugadores_eq, jugadores_eq_validos, seleccionado_eq
        gc.collect()

    except Exception as e:
        st.error(f"Error: {e}")














