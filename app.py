import os
import pandas as pd
import plotly.express as px
import streamlit as st
from src.processor import procesar_resenas
from src.alerts import enviar_alerta_discord

# Configuración básica de la página
st.set_page_config(
    page_title="ReviewRadar AI",
    page_icon="📡",
    layout="wide",
)

RUTA_DEFECTO = "data/resenas_analizadas.csv"

# --- BARRA LATERAL (Carga de datos y filtros) ---
st.sidebar.title("📡 ReviewRadar AI")
st.sidebar.markdown("Analizador automático de reseñas y experiencia de cliente.")
st.sidebar.divider()

st.sidebar.subheader("1. Cargar reseñas")
archivo_subido = st.sidebar.file_uploader(
    "Sube un CSV nuevo (opcional)",
    type=["csv"],
    help="Debe contener las columnas: cliente, plataforma, puntuacion, comentario",
)

# Guardamos los datos en la memoria de la sesión para no perderlos al filtrar
if "df_datos" not in st.session_state:
    if os.path.exists(RUTA_DEFECTO):
        st.session_state.df_datos = pd.read_csv(RUTA_DEFECTO)
    else:
        st.session_state.df_datos = None

# Si el usuario sube un archivo nuevo, mostramos el botón para analizarlo con IA
if archivo_subido is not None:
    if st.sidebar.button("🚀 Analizar con IA ahora", type="primary", use_container_width=True):
        df_nuevo = pd.read_csv(archivo_subido)
        barra = st.sidebar.progress(0, text="Analizando reseñas con Groq...")

        def actualizar_barra(porcentaje):
            barra.progress(porcentaje, text=f"Procesando... {int(porcentaje * 100)}%")

        df_procesado = procesar_resenas(df_nuevo, callback_progreso=actualizar_barra)
        st.session_state.df_datos = df_procesado
        barra.empty()
        st.sidebar.success("¡Análisis completado!")

df = st.session_state.df_datos

# --- PANTALLA PRINCIPAL ---
st.title("📡 ReviewRadar AI — Panel de Operaciones")
st.caption("Detección automática de sentimiento, incidencias críticas y borradores de respuesta con IA.")

if df is None or df.empty:
    st.warning("No hay datos cargados. Sube un archivo CSV en la barra lateral para empezar.")
    st.stop()

# Filtros en la barra lateral
st.sidebar.divider()
st.sidebar.subheader("2. Filtros")

sentimientos_disp = df["sentimiento"].dropna().unique().tolist()
urgencias_disp = df["urgencia"].dropna().unique().tolist()
categorias_disp = df["categoria"].dropna().unique().tolist()

filtro_sent = st.sidebar.multiselect("Sentimiento", sentimientos_disp, default=sentimientos_disp)
filtro_urg = st.sidebar.multiselect("Urgencia", urgencias_disp, default=urgencias_disp)
filtro_cat = st.sidebar.multiselect("Categoría", categorias_disp, default=categorias_disp)

# Aplicamos los filtros a la tabla
df_filtrado = df[
    df["sentimiento"].isin(filtro_sent)
    & df["urgencia"].isin(filtro_urg)
    & df["categoria"].isin(filtro_cat)
]
st.sidebar.divider()
st.sidebar.subheader("3. Alertas al equipo")
if st.sidebar.button("📢 Enviar resumen a Discord", use_container_width=True):
    exito, mensaje = enviar_alerta_discord(df_filtrado)
    if exito:
        st.sidebar.success(mensaje)
    else:
        st.sidebar.error(mensaje)

# --- BLOQUE 1: KPIs (Indicadores clave) ---
total_resenas = len(df_filtrado)
nota_media = df_filtrado["puntuacion"].mean() if total_resenas > 0 else 0
negativas = len(df_filtrado[df_filtrado["sentimiento"] == "Negativo"])
pct_negativas = (negativas / total_resenas * 100) if total_resenas > 0 else 0
urgencia_alta = len(df_filtrado[df_filtrado["urgencia"] == "Alta"])

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Reseñas", total_resenas)
col2.metric("Puntuación Media", f"{nota_media:.1f} / 5 ⭐")
col3.metric("Reseñas Negativas", f"{pct_negativas:.0f}%", f"{negativas} casos", delta_color="inverse")
col4.metric("🚨 Urgencia Alta", urgencia_alta)

st.divider()

# --- BLOQUE 2: GRÁFICOS INTERACTIVOS ---
if total_resenas > 0:
    g1, g2 = st.columns(2)

    with g1:
        st.subheader("Distribución de Sentimiento")
        colores_sent = {
            "Positivo": "#2ecc71",
            "Neutro": "#95a5a6",
            "Negativo": "#e74c3c",
            "Error": "#f39c12",
        }
        fig_sent = px.pie(
            df_filtrado,
            names="sentimiento",
            hole=0.45,
            color="sentimiento",
            color_discrete_map=colores_sent,
        )
        fig_sent.update_layout(margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig_sent, use_container_width=True)

    with g2:
        st.subheader("Incidencias por Categoría")
        conteo_cat = df_filtrado["categoria"].value_counts().reset_index()
        conteo_cat.columns = ["Categoría", "Cantidad"]
        fig_cat = px.bar(
            conteo_cat,
            x="Categoría",
            y="Cantidad",
            color="Categoría",
            text_auto=True,
        )
        fig_cat.update_layout(showlegend=False, margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig_cat, use_container_width=True)

st.divider()

# --- BLOQUE 3: BANDEJA DE RESPUESTAS SUGERIDAS ---
st.subheader("📋 Bandeja de Reseñas y Respuestas Sugeridas")

# Botón para descargar el Excel/CSV filtrado
csv_export = df_filtrado.to_csv(index=False).encode("utf-8-sig")
st.download_button(
    label="⬇️ Descargar informe filtrado (CSV para Excel)",
    data=csv_export,
    file_name="informe_resenas_ia.csv",
    mime="text/csv",
)

# Ordenamos para que salgan primero las de Urgencia Alta
orden_urgencia = {"Alta": 0, "Media": 1, "Baja": 2}
df_ordenado = df_filtrado.copy()
df_ordenado["_orden"] = df_ordenado["urgencia"].map(orden_urgencia).fillna(3)
df_ordenado = df_ordenado.sort_values(by="_orden")

for _, fila in df_ordenado.iterrows():
    icono = "🔴" if fila["urgencia"] == "Alta" else ("🟡" if fila["urgencia"] == "Media" else "🟢")
    titulo = f"{icono} [{fila['urgencia']}] {fila['cliente']} ({fila['puntuacion']}⭐) — {fila['categoria']}: {fila['resumen']}"

    with st.expander(titulo, expanded=(fila["urgencia"] == "Alta")):
        st.markdown(f"**Plataforma:** {fila['plataforma']} | **Fecha:** {fila['fecha']} | **Sentimiento:** `{fila['sentimiento']}`")
        st.info(f"**Comentario del cliente:**\n\n{fila['comentario']}")
        st.markdown("**Respuesta sugerida por IA (lista para copiar):**")
        st.code(fila["respuesta_sugerida"], language=None)