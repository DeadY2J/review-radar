# 🎬 Demo de ReviewRadar AI (60 s)

▶️ Vídeo: [`demo/reviewradar-demo.mp4`](demo/reviewradar-demo.mp4)

## Guion

| Tiempo | En pantalla | Locución |
|---|---|---|
| 0:00 – 0:15 | Subir `resenas_ejemplo.csv` y pulsar **Analizar con IA ahora**; barra de progreso en directo | Procesa cada reseña con la API de Groq y devuelve JSON estructurado. |
| 0:15 – 0:30 | KPIs, gráficos de sentimiento y categorías, filtro por sentimiento | El panel calcula métricas en tiempo real y filtra por sentimiento, categoría o urgencia. |
| 0:30 – 0:45 | Caso de urgencia alta (cobro duplicado), respuesta sugerida y descarga a Excel | Los casos críticos suben arriba con un borrador de respuesta empática; todo se exporta a Excel. |
| 0:45 – 1:00 | **Enviar resumen a Discord** y tarjeta en `#alertas-resenas` | El equipo de operaciones recibe la alerta por webhook (adaptable a Slack o Teams). |

## Texto para portfolio

**ReviewRadar AI**: aplicación en Python + Streamlit que analiza reseñas de clientes con la API de Groq (salida JSON estructurada), clasifica sentimiento, categoría y urgencia, redacta respuestas empáticas y avisa al equipo de operaciones por webhook en Discord. Reduce el triaje de un lote de reseñas de minutos de trabajo manual a segundos y exporta informes filtrados a Excel.
