import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()


def enviar_alerta_discord(df: pd.DataFrame) -> tuple[bool, str]:
    """
    Genera un resumen ejecutivo de las reseñas filtradas y lo envía
    a Discord mediante un Webhook en formato tarjeta (Embed).
    """
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")

    if not webhook_url:
        return False, "No se encontró DISCORD_WEBHOOK_URL en el archivo .env"

    if df is None or df.empty:
        return False, "No hay reseñas para enviar."

    # Calculamos las métricas principales
    total = len(df)
    nota_media = df["puntuacion"].mean()
    negativas = len(df[df["sentimiento"] == "Negativo"])
    df_urgentes = df[df["urgencia"] == "Alta"]
    num_urgentes = len(df_urgentes)

    # Preparamos el listado de casos críticos (máximo 5 para no saturar el mensaje)
    if num_urgentes > 0:
        lineas_urgentes = []
        for _, fila in df_urgentes.head(5).iterrows():
            lineas_urgentes.append(
                f"• **{fila['cliente']}** ({fila['categoria']}): {fila['resumen']}"
            )
        texto_urgentes = "\n".join(lineas_urgentes)
        color_tarjeta = 15158332  # Rojo (hay alertas críticas)
    else:
        texto_urgentes = "Sin incidencias de urgencia alta en este lote."
        color_tarjeta = 3066993  # Verde (todo bajo control)

    # Estructura estándar de tarjeta (Embed) que entiende Discord
    payload = {
        "username": "ReviewRadar AI",
        "embeds": [
            {
                "title": "📡 Resumen Ejecutivo — ReviewRadar AI",
                "color": color_tarjeta,
                "fields": [
                    {"name": "📊 Total analizadas", "value": str(total), "inline": True},
                    {"name": "⭐ Nota media", "value": f"{nota_media:.1f} / 5", "inline": True},
                    {"name": "🚨 Urgencia alta", "value": f"{num_urgentes} casos ({negativas} neg.)", "inline": True},
                    {"name": "🔥 Casos críticos a revisar ya", "value": texto_urgentes, "inline": False},
                ],
                "footer": {"text": "Generado automáticamente por ReviewRadar AI"},
            }
        ],
    }

    try:
        respuesta = requests.post(webhook_url, json=payload, timeout=10)
        # Discord devuelve código 204 cuando el mensaje se entrega bien
        if respuesta.status_code in (200, 204):
            return True, "Resumen enviado correctamente a Discord."
        return False, f"Error de Discord (código {respuesta.status_code})."
    except Exception as e:
        return False, f"Error de conexión: {str(e)}"