import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json


# ---------- GET /perfil ----------

def test_perfil_usuario_sin_datos_devuelve_ceros(logged_in_client):
    resp = logged_in_client.get("/perfil")
    assert resp.status_code == 200
    assert resp.get_json() == {
        "usuario": "admin", "limite": None, "usadas": 0,
        "auditorias": 0, "clientes": 0, "proyectos": 0
    }


def test_perfil_cuenta_solo_datos_del_usuario(logged_in_client):
    with open("historial.json", "w", encoding="utf-8") as f:
        json.dump([{"usuario": "admin"}, {"usuario": "otro"}], f)
    with open("clientes.json", "w", encoding="utf-8") as f:
        json.dump([{"usuario": "admin"}, {"usuario": "otro"}], f)
    with open("proyectos.json", "w", encoding="utf-8") as f:
        json.dump([{"usuario": "admin"}, {"usuario": "otro"}], f)

    resp = logged_in_client.get("/perfil")
    datos = resp.get_json()
    assert datos["auditorias"] == 1
    assert datos["clientes"] == 1
    assert datos["proyectos"] == 1


def test_perfil_refleja_limite_y_usadas_del_usuario(client):
    with open("auth.json", "w", encoding="utf-8") as f:
        json.dump({"limitado": {"password": "irrelevante", "limite": 10, "usadas": 3}}, f)
    with client.session_transaction() as sess:
        sess["usuario"] = "limitado"

    resp = client.get("/perfil")
    datos = resp.get_json()
    assert datos["limite"] == 10
    assert datos["usadas"] == 3


# ---------- GET /resumen ----------

def test_resumen_sin_datos_devuelve_ceros(logged_in_client):
    resp = logged_in_client.get("/resumen")
    assert resp.status_code == 200
    assert resp.get_json() == {
        "facturado": 0, "clientes_activos": 0, "auditorias": 0,
        "cerrados": 0, "negociacion": 0
    }
    with open("facturado.json", encoding="utf-8") as f:
        facturado = json.load(f)
    assert facturado["admin"] == {"total": 0, "registrados": {}}


def test_resumen_calcula_facturado_desde_clientes_cerrados(logged_in_client):
    with open("clientes.json", "w", encoding="utf-8") as f:
        json.dump([
            {"nombre": "A", "usuario": "admin", "cerrado_en": 1000},
            {"nombre": "B", "usuario": "admin", "cerrado_en": 500},
            {"nombre": "C", "usuario": "otro", "cerrado_en": 9999},
        ], f)

    resp = logged_in_client.get("/resumen")
    datos = resp.get_json()
    assert datos["facturado"] == 1500
    assert datos["clientes_activos"] == 2


def test_resumen_no_duplica_facturado_en_llamados_repetidos(logged_in_client):
    with open("clientes.json", "w", encoding="utf-8") as f:
        json.dump([{"nombre": "A", "usuario": "admin", "cerrado_en": 1000}], f)

    primera = logged_in_client.get("/resumen").get_json()
    segunda = logged_in_client.get("/resumen").get_json()

    assert primera["facturado"] == 1000
    assert segunda["facturado"] == 1000


def test_resumen_actualiza_facturado_si_cambia_cerrado_en(logged_in_client):
    with open("clientes.json", "w", encoding="utf-8") as f:
        json.dump([{"nombre": "A", "usuario": "admin", "cerrado_en": 1000}], f)
    logged_in_client.get("/resumen")

    with open("clientes.json", "w", encoding="utf-8") as f:
        json.dump([{"nombre": "A", "usuario": "admin", "cerrado_en": 1500}], f)
    resp = logged_in_client.get("/resumen")

    assert resp.get_json()["facturado"] == 1500


def test_resumen_cuenta_cerrados_y_negociacion(logged_in_client):
    with open("clientes.json", "w", encoding="utf-8") as f:
        json.dump([
            {"nombre": "A", "usuario": "admin", "estado": "cerrado"},
            {"nombre": "B", "usuario": "admin", "estado": "en negociación"},
            {"nombre": "C", "usuario": "admin", "estado": "contactado"},
        ], f)

    resp = logged_in_client.get("/resumen")
    datos = resp.get_json()
    assert datos["cerrados"] == 1
    assert datos["negociacion"] == 1


def test_resumen_cuenta_auditorias_desde_historial(logged_in_client):
    with open("historial.json", "w", encoding="utf-8") as f:
        json.dump([{"usuario": "admin"}, {"usuario": "admin"}, {"usuario": "otro"}], f)

    resp = logged_in_client.get("/resumen")
    assert resp.get_json()["auditorias"] == 2
