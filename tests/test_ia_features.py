import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from unittest.mock import patch


# ---------- POST /analizar-web ----------

def test_analizar_web_camino_feliz(logged_in_client):
    resultado_fake = {
        "ok": True,
        "oportunidad_web": "Alta",
        "señales": {
            "formulario_contacto": False, "email_visible": False,
            "whatsapp": False, "https": True, "favicon": True,
        },
    }
    with patch("app.analizar_web", return_value=resultado_fake) as mock_analizar:
        resp = logged_in_client.post("/analizar-web", json={"web": "https://ejemplo.com"})

    assert resp.status_code == 200
    assert resp.get_json() == resultado_fake
    mock_analizar.assert_called_once_with("https://ejemplo.com")


def test_analizar_web_error_502(logged_in_client):
    with patch("app.analizar_web", return_value={"ok": False, "error": "No se pudo conectar con el sitio."}):
        resp = logged_in_client.post("/analizar-web", json={"web": "https://ejemplo.com"})

    assert resp.status_code == 502
    assert resp.get_json() == {"error": "No se pudo conectar con el sitio."}


def test_analizar_web_sin_web_400(logged_in_client):
    with patch("app.analizar_web") as mock_analizar:
        resp = logged_in_client.post("/analizar-web", json={"web": "No tiene"})

    assert resp.status_code == 400
    assert "no tiene sitio web" in resp.get_json()["error"]
    mock_analizar.assert_not_called()


def test_analizar_web_sin_campo_web_400(logged_in_client):
    with patch("app.analizar_web") as mock_analizar:
        resp = logged_in_client.post("/analizar-web", json={})

    assert resp.status_code == 400
    mock_analizar.assert_not_called()


# ---------- POST /generar-propuesta ----------

def test_generar_propuesta_camino_feliz(logged_in_client):
    lead = {"nombre": "Panadería López", "tiene_web": False}
    with patch("app.generar_propuesta", return_value={"ok": True, "texto": "Hola, te escribo porque..."}) as mock_generar:
        resp = logged_in_client.post("/generar-propuesta", json={"formato": "whatsapp", "lead": lead})

    assert resp.status_code == 200
    assert resp.get_json() == {"texto": "Hola, te escribo porque..."}
    mock_generar.assert_called_once_with(lead, "whatsapp")


def test_generar_propuesta_usa_formato_por_defecto(logged_in_client):
    with patch("app.generar_propuesta", return_value={"ok": True, "texto": "Hola"}) as mock_generar:
        logged_in_client.post("/generar-propuesta", json={"lead": {"nombre": "X"}})

    mock_generar.assert_called_once_with({"nombre": "X"}, "whatsapp")


def test_generar_propuesta_error_502(logged_in_client):
    with patch("app.generar_propuesta", return_value={"ok": False, "error": "No se pudo conectar con el servicio de IA."}):
        resp = logged_in_client.post("/generar-propuesta", json={"lead": {"nombre": "X"}})

    assert resp.status_code == 502
    assert resp.get_json() == {"error": "No se pudo conectar con el servicio de IA."}
