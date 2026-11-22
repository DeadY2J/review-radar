import json
from types import SimpleNamespace

from src import analyzer


def _respuesta_falsa(contenido):
    mensaje = SimpleNamespace(content=contenido)
    return SimpleNamespace(choices=[SimpleNamespace(message=mensaje)])


def _cliente_falso(contenido=None, error=None):
    def crear(**kwargs):
        if error:
            raise error
        return _respuesta_falsa(contenido)

    return SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=crear)))


def test_normalizar_acepta_resultado_valido():
    datos = {
        "sentimiento": "Negativo",
        "categoria": "Envío",
        "urgencia": "Alta",
        "resumen": " Paquete perdido ",
        "respuesta_sugerida": "Lo sentimos mucho.",
    }
    res = analyzer.normalizar_resultado(datos)
    assert res["urgencia"] == "Alta"
    assert res["resumen"] == "Paquete perdido"


def test_normalizar_corrige_valores_desconocidos():
    res = analyzer.normalizar_resultado(
        {"sentimiento": "Neutro", "categoria": "Logística", "urgencia": "Crítica"}
    )
    assert res["categoria"] == "Otro"
    assert res["urgencia"] == "Media"
    assert res["resumen"] == ""
    assert res["respuesta_sugerida"] == ""


def test_normalizar_rechaza_sentimiento_invalido():
    res = analyzer.normalizar_resultado({"sentimiento": "Furioso"})
    assert res["sentimiento"] == "Error"


def test_normalizar_rechaza_lo_que_no_es_un_objeto():
    assert analyzer.normalizar_resultado(["a", "b"])["sentimiento"] == "Error"


def test_analizar_resena_devuelve_resultado_normalizado(monkeypatch):
    contenido = json.dumps(
        {"sentimiento": "Positivo", "categoria": "Producto", "urgencia": "Baja",
         "resumen": "Elogio", "respuesta_sugerida": "Gracias"}
    )
    monkeypatch.setattr(analyzer, "_get_cliente", lambda: _cliente_falso(contenido))
    res = analyzer.analizar_resena("Genial", 5)
    assert res["sentimiento"] == "Positivo"


def test_analizar_resena_no_se_rompe_con_json_invalido(monkeypatch):
    monkeypatch.setattr(analyzer, "_get_cliente", lambda: _cliente_falso("esto no es json"))
    res = analyzer.analizar_resena("Genial", 5)
    assert res["sentimiento"] == "Error"
    assert res["urgencia"] == "Baja"


def test_analizar_resena_oculta_detalles_del_error(monkeypatch):
    error = ConnectionError("https://api.groq.com/clave-secreta")
    monkeypatch.setattr(analyzer, "_get_cliente", lambda: _cliente_falso(error=error))
    res = analyzer.analizar_resena("Genial", 5)
    assert res["sentimiento"] == "Error"
    assert "clave-secreta" not in res["resumen"]
    assert "ConnectionError" in res["resumen"]


def test_sin_clave_da_un_mensaje_claro(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.setattr(analyzer, "_cliente", None)
    res = analyzer.analizar_resena("Genial", 5)
    assert res["sentimiento"] == "Error"
    assert "GROQ_API_KEY" in res["resumen"]
