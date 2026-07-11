import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import pytest

import app as app_module


@pytest.fixture
def client(tmp_path, monkeypatch):
    """Cliente de test con cada archivo de datos (auth.json, historial.json,
    clientes.json, etc.) aislado en un directorio temporal por test, para no
    leer ni escribir los datos reales del proyecto."""
    monkeypatch.chdir(tmp_path)
    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as test_client:
        yield test_client


@pytest.fixture
def logged_in_client(client):
    """Cliente ya autenticado como el usuario 'admin' por defecto (creado
    automáticamente por cargar_auth() la primera vez que se lee auth.json)."""
    with client.session_transaction() as sess:
        sess["usuario"] = "admin"
    return client
