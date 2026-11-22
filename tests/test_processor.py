import pandas as pd

from src import processor


def _falso_analisis(comentario, puntuacion):
    return {
        "sentimiento": "Positivo",
        "categoria": "Otro",
        "urgencia": "Baja",
        "resumen": comentario[:10],
        "respuesta_sugerida": "Gracias",
    }


def test_procesar_resenas_anade_columnas_y_progreso(monkeypatch):
    monkeypatch.setattr(processor, "analizar_resena", _falso_analisis)
    monkeypatch.setattr(processor.time, "sleep", lambda s: None)
    df = pd.DataFrame(
        {"cliente": ["Ana", "Luis"], "puntuacion": [5, 4], "comentario": ["Muy bien", "Bien"]}
    )
    progreso = []
    resultado = processor.procesar_resenas(df, callback_progreso=progreso.append)
    assert list(resultado["sentimiento"]) == ["Positivo", "Positivo"]
    assert progreso == [0.5, 1.0]


def test_progreso_correcto_con_indice_no_consecutivo(monkeypatch):
    monkeypatch.setattr(processor, "analizar_resena", _falso_analisis)
    monkeypatch.setattr(processor.time, "sleep", lambda s: None)
    df = pd.DataFrame(
        {"cliente": ["Ana", "Luis"], "puntuacion": [5, 4], "comentario": ["Muy bien", "Bien"]},
        index=[10, 20],
    )
    progreso = []
    processor.procesar_resenas(df, callback_progreso=progreso.append)
    assert progreso == [0.5, 1.0]
