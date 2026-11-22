import pandas as pd

from src import alerts


def _df(urgentes=1):
    filas = []
    for i in range(urgentes):
        filas.append(
            {"cliente": f"Cliente {i}", "puntuacion": 1, "sentimiento": "Negativo",
             "urgencia": "Alta", "categoria": "Envío", "resumen": "x" * 300}
        )
    filas.append(
        {"cliente": "Ana", "puntuacion": 5, "sentimiento": "Positivo",
         "urgencia": "Baja", "categoria": "Producto", "resumen": "Todo bien"}
    )
    return pd.DataFrame(filas)


def test_sin_webhook_devuelve_error(monkeypatch):
    monkeypatch.delenv("DISCORD_WEBHOOK_URL", raising=False)
    ok, mensaje = alerts.enviar_alerta_discord(_df())
    assert not ok
    assert "DISCORD_WEBHOOK_URL" in mensaje


def test_dataframe_vacio(monkeypatch):
    monkeypatch.setenv("DISCORD_WEBHOOK_URL", "https://example.test/hook")
    ok, _ = alerts.enviar_alerta_discord(pd.DataFrame())
    assert not ok


def test_envio_correcto_y_payload_seguro(monkeypatch):
    monkeypatch.setenv("DISCORD_WEBHOOK_URL", "https://example.test/hook")
    enviado = {}

    def post_falso(url, json, timeout):
        enviado["url"], enviado["json"] = url, json
        return type("R", (), {"status_code": 204})()

    monkeypatch.setattr(alerts.requests, "post", post_falso)
    ok, _ = alerts.enviar_alerta_discord(_df(urgentes=5))
    assert ok
    assert enviado["json"]["allowed_mentions"] == {"parse": []}
    campos = enviado["json"]["embeds"][0]["fields"]
    assert all(len(c["value"]) <= 1024 for c in campos)


def test_error_http_de_discord(monkeypatch):
    monkeypatch.setenv("DISCORD_WEBHOOK_URL", "https://example.test/hook")
    monkeypatch.setattr(
        alerts.requests, "post", lambda url, json, timeout: type("R", (), {"status_code": 400})()
    )
    ok, mensaje = alerts.enviar_alerta_discord(_df())
    assert not ok
    assert "400" in mensaje
