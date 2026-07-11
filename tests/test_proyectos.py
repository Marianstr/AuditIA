import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json


def test_proyectos_get_vacio_devuelve_lista_vacia(logged_in_client):
    resp = logged_in_client.get("/proyectos")
    assert resp.status_code == 200
    assert resp.get_json() == []


def test_proyectos_post_agrega_proyecto(logged_in_client):
    resp = logged_in_client.post("/proyectos", json={"nombre": "Campaña Madrid"})
    assert resp.status_code == 200
    assert resp.get_json() == {"ok": True}

    proyectos = logged_in_client.get("/proyectos").get_json()
    assert len(proyectos) == 1
    assert proyectos[0]["nombre"] == "Campaña Madrid"
    assert "fecha" in proyectos[0]


def test_proyectos_get_filtra_por_usuario(logged_in_client):
    with open("proyectos.json", "w", encoding="utf-8") as f:
        json.dump([{"nombre": "De otro usuario", "usuario": "otro"}], f)
    logged_in_client.post("/proyectos", json={"nombre": "Mío"})

    proyectos = logged_in_client.get("/proyectos").get_json()
    assert len(proyectos) == 1
    assert proyectos[0]["nombre"] == "Mío"


def _seed_historial(entradas):
    with open("historial.json", "w", encoding="utf-8") as f:
        json.dump(entradas, f)


def test_asignar_proyecto_a_auditoria_propia(logged_in_client):
    _seed_historial([{"tipo": "floristerias", "ciudad": "madrid", "usuario": "admin", "proyecto": ""}])
    resp = logged_in_client.post("/asignar-proyecto", json={"indice": 0, "proyecto": "Campaña Madrid"})
    assert resp.status_code == 200

    with open("historial.json", encoding="utf-8") as f:
        historial = json.load(f)
    assert historial[0]["proyecto"] == "Campaña Madrid"


def test_asignar_proyecto_no_afecta_auditoria_ajena(logged_in_client):
    _seed_historial([{"tipo": "floristerias", "ciudad": "madrid", "usuario": "otro", "proyecto": ""}])
    resp = logged_in_client.post("/asignar-proyecto", json={"indice": 0, "proyecto": "Campaña Madrid"})
    assert resp.status_code == 200

    with open("historial.json", encoding="utf-8") as f:
        historial = json.load(f)
    assert historial[0]["proyecto"] == ""


def test_asignar_proyecto_indice_invalido_no_rompe(logged_in_client):
    _seed_historial([])
    resp = logged_in_client.post("/asignar-proyecto", json={"indice": 99, "proyecto": "X"})
    assert resp.status_code == 200
    assert resp.get_json() == {"ok": True}


def test_borrar_proyecto_elimina_y_limpia_historial(logged_in_client):
    logged_in_client.post("/proyectos", json={"nombre": "Campaña Madrid"})
    _seed_historial([{"tipo": "floristerias", "ciudad": "madrid", "usuario": "admin", "proyecto": "Campaña Madrid"}])

    resp = logged_in_client.post("/borrar-proyecto", json={"nombre": "Campaña Madrid"})
    assert resp.status_code == 200

    assert logged_in_client.get("/proyectos").get_json() == []
    with open("historial.json", encoding="utf-8") as f:
        historial = json.load(f)
    assert historial[0]["proyecto"] == ""


def test_borrar_proyecto_no_afecta_otro_usuario(logged_in_client):
    with open("proyectos.json", "w", encoding="utf-8") as f:
        json.dump([{"nombre": "Campaña Madrid", "usuario": "otro"}], f)

    resp = logged_in_client.post("/borrar-proyecto", json={"nombre": "Campaña Madrid"})
    assert resp.status_code == 200

    with open("proyectos.json", encoding="utf-8") as f:
        proyectos = json.load(f)
    assert len(proyectos) == 1
    assert proyectos[0]["usuario"] == "otro"


def test_asignar_proyecto_sin_historial_no_rompe(logged_in_client):
    resp = logged_in_client.post("/asignar-proyecto", json={"indice": 0, "proyecto": "X"})
    assert resp.status_code == 200
    assert resp.get_json() == {"ok": True}
    assert not os.path.exists("historial.json")


def test_borrar_proyecto_sin_archivos_no_rompe(logged_in_client):
    resp = logged_in_client.post("/borrar-proyecto", json={"nombre": "Campaña Madrid"})
    assert resp.status_code == 200
    assert resp.get_json() == {"ok": True}

    with open("proyectos.json", encoding="utf-8") as f:
        assert json.load(f) == []
    assert not os.path.exists("historial.json")
