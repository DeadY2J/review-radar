import time
import pandas as pd
from src.analyzer import analizar_resena


def procesar_resenas(df: pd.DataFrame, callback_progreso=None) -> pd.DataFrame:
    """
    Recibe una tabla (DataFrame) con reseñas, analiza cada una con IA
    y devuelve una nueva tabla con las 5 columnas de resultados añadidas.
    """
    resultados = []
    total = len(df)

    # Recorremos el CSV fila por fila
    for indice, fila in df.iterrows():
        comentario = str(fila["comentario"])
        puntuacion = int(fila["puntuacion"])

        print(f"Analizando reseña {indice + 1}/{total} ({fila['cliente']})...")
        analisis = analizar_resena(comentario, puntuacion)
        resultados.append(analisis)

        # Si hay una barra de progreso conectada (la usaremos en Streamlit), la actualizamos
        if callback_progreso:
            callback_progreso((indice + 1) / total)

        # Pequeña pausa de medio segundo para no saturar el límite gratuito de la API
        time.sleep(0.5)

    # Convertimos la lista de resultados JSON en una tabla de pandas
    df_analisis = pd.DataFrame(resultados)

    # Unimos la tabla original (izquierda) con las nuevas columnas de IA (derecha)
    df_final = pd.concat([df.reset_index(drop=True), df_analisis], axis=1)
    return df_final


# Bloque de prueba: procesa nuestro archivo de ejemplo y guarda el resultado
if __name__ == "__main__":
    ruta_entrada = "data/resenas_ejemplo.csv"
    ruta_salida = "data/resenas_analizadas.csv"

    print(f"Leyendo archivo: {ruta_entrada}\n")
    df_original = pd.read_csv(ruta_entrada)

    df_resultado = procesar_resenas(df_original)

    # Guardamos el resultado en un nuevo CSV (utf-8-sig hace que Excel abra bien las tildes)
    df_resultado.to_csv(ruta_salida, index=False, encoding="utf-8-sig")

    print(f"\n¡Listo! Resultados guardados en: {ruta_salida}\n")
    print("Resumen rápido de sentimientos detectados:")
    print(df_resultado["sentimiento"].value_counts())