import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json


def test_landing_no_requiere_login(client):
    resp = client.get("/")
    assert resp.status_code == 200


def test_app_sin_sesion_redirige_a_login(client):
    resp = client.get("/app")
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]


def test_app_con_sesion_renderiza_panel(logged_in_client):
    resp = logged_in_client.get("/app")
    assert resp.status_code == 200


def test_login_get_muestra_formulario(client):
    resp = client.get("/login")
    assert resp.status_code == 200


def test_login_exitoso_crea_sesion_y_redirige(client):
    resp = client.post("/login", data={"usuario": "admin", "password": "auditia2026"})
    assert resp.status_code == 302
    assert "/app" in resp.headers["Location"]
    with client.session_transaction() as sess:
        assert sess["usuario"] == "admin"


def test_login_password_incorrecta_no_crea_sesion(client):
    resp = client.post("/login", data={"usuario": "admin", "password": "incorrecta"})
    assert resp.status_code == 200
    assert "incorrectos" in resp.get_data(as_text=True)
    with client.session_transaction() as sess:
        assert "usuario" not in sess


def test_login_usuario_inexistente_no_crea_sesion(client):
    resp = client.post("/login", data={"usuario": "no_existe", "password": "lo_que_sea"})
    assert resp.status_code == 200
    assert "incorrectos" in resp.get_data(as_text=True)
    with client.session_transaction() as sess:
        assert "usuario" not in sess


def test_logout_limpia_sesion_y_redirige(logged_in_client):
    resp = logged_in_client.get("/logout")
    assert resp.status_code == 302
    with logged_in_client.session_transaction() as sess:
        assert "usuario" not in sess


def test_registro_exitoso_crea_usuario_y_loguea(client):
    resp = client.post("/registro", data={"email": "nuevo@ejemplo.com", "password": "123456"})
    assert resp.status_code == 302
    assert "/app" in resp.headers["Location"]
    with client.session_transaction() as sess:
        assert sess["usuario"] == "nuevo@ejemplo.com"
    with open("auth.json", encoding="utf-8") as f:
        auth = json.load(f)
    assert auth["nuevo@ejemplo.com"]["limite"] == 5


def test_registro_email_duplicado_muestra_error(client):
    client.post("/registro", data={"email": "dup@ejemplo.com", "password": "123456"})
    with client.session_transaction() as sess:
        sess.clear()
    resp = client.post("/registro", data={"email": "dup@ejemplo.com", "password": "otraclave"})
    assert resp.status_code == 200
    assert "ya está registrado" in resp.get_data(as_text=True)


def test_registro_email_invalido_muestra_error(client):
    resp = client.post("/registro", data={"email": "no-es-un-email", "password": "123456"})
    assert resp.status_code == 200
    assert "email válido" in resp.get_data(as_text=True)


def test_registro_password_corta_muestra_error(client):
    resp = client.post("/registro", data={"email": "corta@ejemplo.com", "password": "123"})
    assert resp.status_code == 200
    assert "al menos 6 caracteres" in resp.get_data(as_text=True)
