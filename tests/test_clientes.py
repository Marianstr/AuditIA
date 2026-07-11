import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json


def test_clientes_get_vacio_devuelve_lista_vacia(logged_in_client):
    resp = logged_in_client.get("/clientes")
    assert resp.status_code == 200
    assert resp.get_json() == []


def test_clientes_post_agrega_cliente(logged_in_client):
    resp = logged_in_client.post("/clientes", json={"nombre": "Panadería López", "direccion": "Calle Falsa 123"})
    assert resp.status_code == 200
    assert resp.get_json() == {"ok": True}

    clientes = logged_in_client.get("/clientes").get_json()
    assert len(clientes) == 1
    assert clientes[0]["nombre"] == "Panadería López"
    assert clientes[0]["estado"] == "contactado"
    assert "fecha_agregado" in clientes[0]


def test_clientes_get_filtra_por_usuario(logged_in_client):
    with open("clientes.json", "w", encoding="utf-8") as f:
        json.dump([{"nombre": "De otro usuario", "usuario": "otro"}], f)
    logged_in_client.post("/clientes", json={"nombre": "Mío"})

    clientes = logged_in_client.get("/clientes").get_json()
    assert len(clientes) == 1
    assert clientes[0]["nombre"] == "Mío"


def test_clientes_estado_cambia_estado(logged_in_client):
    logged_in_client.post("/clientes", json={"nombre": "Cliente X"})
    resp = logged_in_client.post("/clientes/estado", json={"nombre": "Cliente X", "estado": "cerrado"})
    assert resp.status_code == 200
    assert resp.get_json() == {"ok": True}

    clientes = logged_in_client.get("/clientes").get_json()
    assert clientes[0]["estado"] == "cerrado"


def test_clientes_estado_sin_archivo_404(logged_in_client):
    resp = logged_in_client.post("/clientes/estado", json={"nombre": "X", "estado": "cerrado"})
    assert resp.status_code == 404
    assert resp.get_json() == {"ok": False}


def test_clientes_presupuesto_actualiza_campos(logged_in_client):
    logged_in_client.post("/clientes", json={"nombre": "Cliente X"})
    resp = logged_in_client.post("/clientes/presupuesto", json={"nombre": "Cliente X", "presupuesto": 1000, "cerrado_en": 500})
    assert resp.status_code == 200

    clientes = logged_in_client.get("/clientes").get_json()
    assert clientes[0]["presupuesto"] == 1000
    assert clientes[0]["cerrado_en"] == 500


def test_clientes_presupuesto_sin_archivo_404(logged_in_client):
    resp = logged_in_client.post("/clientes/presupuesto", json={"nombre": "X", "presupuesto": 1})
    assert resp.status_code == 404


def test_clientes_borrar_uno(logged_in_client):
    logged_in_client.post("/clientes", json={"nombre": "A"})
    logged_in_client.post("/clientes", json={"nombre": "B"})
    resp = logged_in_client.post("/clientes/borrar", json={"nombre": "A"})
    assert resp.status_code == 200

    nombres = [c["nombre"] for c in logged_in_client.get("/clientes").get_json()]
    assert nombres == ["B"]


def test_clientes_borrar_todo_solo_afecta_al_usuario(logged_in_client):
    with open("clientes.json", "w", encoding="utf-8") as f:
        json.dump([{"nombre": "De otro usuario", "usuario": "otro"}], f)
    logged_in_client.post("/clientes", json={"nombre": "Mío"})

    resp = logged_in_client.post("/clientes/borrar", json={"todo": True})
    assert resp.status_code == 200

    with open("clientes.json", encoding="utf-8") as f:
        restantes = json.load(f)
    assert len(restantes) == 1
    assert restantes[0]["nombre"] == "De otro usuario"


def test_clientes_borrar_sin_archivo_404(logged_in_client):
    resp = logged_in_client.post("/clientes/borrar", json={"nombre": "X"})
    assert resp.status_code == 404
