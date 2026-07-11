import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
from unittest.mock import patch

NEGOCIO_FAKE = {
    "nombre": "Panadería López", "direccion": "Calle Falsa 123", "telefono": "666111222",
    "web": "No tiene", "rating": 3.0, "cantidad_resenas": 5, "tiene_sitio_web": False,
}


def test_buscar_camino_feliz_por_categoria(logged_in_client):
    with patch("app.buscar_negocios_google", return_value=[NEGOCIO_FAKE]) as mock_buscar:
        resp = logged_in_client.post("/buscar", json={"modo": "categoria", "tipo": "panaderias", "ciudad": "madrid", "zona": ""})

    assert resp.status_code == 200
    datos = resp.get_json()
    assert datos["indice"] == 0
    assert len(datos["resultados"]) == 1
    assert datos["resultados"][0]["nombre"] == "Panadería López"
    assert datos["resultados"][0]["clasificacion"] == "caliente"
    mock_buscar.assert_called_once_with("panaderias", "madrid", "")

    with open("historial.json", encoding="utf-8") as f:
        historial = json.load(f)
    assert len(historial) == 1
    assert historial[0]["usuario"] == "admin"
    assert historial[0]["modo"] == "categoria"
    assert historial[0]["tipo"] == "panaderias"

    with open("auth.json", encoding="utf-8") as f:
        auth = json.load(f)
    assert auth["admin"]["usadas"] == 1


def test_buscar_camino_feliz_por_nombre(logged_in_client):
    with patch("app.buscar_negocios_google", return_value=[NEGOCIO_FAKE]) as mock_buscar:
        resp = logged_in_client.post("/buscar", json={"modo": "nombre", "nombre_negocio": "Panadería López"})

    assert resp.status_code == 200
    mock_buscar.assert_called_once_with(consulta_directa="Panadería López")

    with open("historial.json", encoding="utf-8") as f:
        historial = json.load(f)
    assert historial[0]["modo"] == "nombre"
    assert historial[0]["tipo"] == "Panadería López"
    assert historial[0]["ciudad"] == ""


def test_buscar_limite_alcanzado_403(client):
    with open("auth.json", "w", encoding="utf-8") as f:
        json.dump({"limitado": {"password": "irrelevante", "limite": 1, "usadas": 1}}, f)
    with client.session_transaction() as sess:
        sess["usuario"] = "limitado"

    with patch("app.buscar_negocios_google") as mock_buscar:
        resp = client.post("/buscar", json={"modo": "categoria", "tipo": "x", "ciudad": "y", "zona": ""})

    assert resp.status_code == 403
    assert "límite" in resp.get_json()["error"]
    mock_buscar.assert_not_called()


def test_buscar_error_de_google_502(logged_in_client):
    with patch("app.buscar_negocios_google", side_effect=Exception("fallo de red")):
        resp = logged_in_client.post("/buscar", json={"modo": "categoria", "tipo": "x", "ciudad": "y", "zona": ""})

    assert resp.status_code == 502
    assert "Ocurrió un error" in resp.get_json()["error"]

    with open("auth.json", encoding="utf-8") as f:
        auth = json.load(f)
    assert auth["admin"]["usadas"] == 0
    assert not os.path.exists("historial.json")


def test_buscar_agrega_a_historial_existente(logged_in_client):
    with open("historial.json", "w", encoding="utf-8") as f:
        json.dump([{"tipo": "previa", "usuario": "admin"}], f)

    with patch("app.buscar_negocios_google", return_value=[NEGOCIO_FAKE]):
        resp = logged_in_client.post("/buscar", json={"modo": "categoria", "tipo": "panaderias", "ciudad": "madrid", "zona": ""})

    assert resp.status_code == 200
    assert resp.get_json()["indice"] == 1

    with open("historial.json", encoding="utf-8") as f:
        historial = json.load(f)
    assert len(historial) == 2
    assert historial[0]["tipo"] == "previa"
    assert historial[1]["tipo"] == "panaderias"
