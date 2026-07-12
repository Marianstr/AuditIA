import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import app as app_module


# ---------------------------------------------------------------------------
# plan_de: deduce el plan del usuario a partir de su registro
# ---------------------------------------------------------------------------

def test_plan_de_sin_usuario_es_free():
    assert app_module.plan_de(None) == "free"


def test_plan_de_campo_plan_explicito_tiene_prioridad():
    # Aunque el limite sea bajo, el campo "plan" explícito manda.
    assert app_module.plan_de({"plan": "agency", "limite": 5}) == "agency"


def test_plan_de_limite_none_es_agency():
    # Sin límite = búsquedas ilimitadas (admin) = plan más alto.
    assert app_module.plan_de({"limite": None}) == "agency"


def test_plan_de_limite_alto_es_agency():
    assert app_module.plan_de({"limite": 200}) == "agency"


def test_plan_de_limite_medio_es_pro():
    assert app_module.plan_de({"limite": 50}) == "pro"


def test_plan_de_limite_bajo_es_free():
    assert app_module.plan_de({"limite": 5}) == "free"


# ---------------------------------------------------------------------------
# plan_permite: True si el plan del usuario incluye la función
# ---------------------------------------------------------------------------

def test_plan_permite_agency_incluye_propuesta_visual():
    assert app_module.plan_permite({"plan": "agency"}, "propuesta_visual") is True


def test_plan_permite_pro_incluye_crm():
    assert app_module.plan_permite({"limite": 50}, "crm") is True


def test_plan_permite_free_no_incluye_crm():
    assert app_module.plan_permite({"limite": 5}, "crm") is False


def test_plan_permite_free_no_incluye_propuesta_visual():
    assert app_module.plan_permite({"limite": 5}, "propuesta_visual") is False


# ---------------------------------------------------------------------------
# Ruta /mockup: exclusiva de planes con "propuesta_visual" (Pro/Agency)
# La búsqueda de foto en Pexels se mockea para no depender de la red.
# ---------------------------------------------------------------------------

def test_mockup_agency_devuelve_200(logged_in_client, monkeypatch):
    monkeypatch.setattr(app_module, "buscar_foto_categoria", lambda categoria: None)
    resp = logged_in_client.get("/mockup?nombre=Flores Bella&categoria=floristeria")
    assert resp.status_code == 200
    # El nombre del negocio aparece en el mockup renderizado.
    assert "Flores Bella" in resp.get_data(as_text=True)


def test_mockup_usa_foto_de_pexels_cuando_hay(logged_in_client, monkeypatch):
    foto = "https://images.pexels.com/photos/1/foto.jpeg"
    monkeypatch.setattr(app_module, "buscar_foto_categoria", lambda categoria: foto)
    resp = logged_in_client.get("/mockup?nombre=Test&categoria=floristeria")
    assert resp.status_code == 200
    assert foto in resp.get_data(as_text=True)


def test_mockup_free_devuelve_403(client, monkeypatch):
    monkeypatch.setattr(app_module, "buscar_foto_categoria", lambda categoria: None)
    with client.session_transaction() as sess:
        sess["usuario"] = "visitante"
    resp = client.get("/mockup?nombre=Test&categoria=floristeria")
    assert resp.status_code == 403


def test_mockup_sin_login_redirige(client):
    resp = client.get("/mockup?nombre=Test&categoria=floristeria")
    # Sin sesión, @login_required no deja pasar (redirección o 401/403).
    assert resp.status_code in (301, 302, 401, 403)
