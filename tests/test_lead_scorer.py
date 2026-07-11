import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scoring.lead_scorer import calcular_score, clasificar_lead, recomendar_servicios


def test_lead_sin_web_sin_rating_sin_resenas():
    lead = {
        "tiene_sitio_web": False,
        "rating": 3.0,
        "cantidad_resenas": 5
    }
    assert calcular_score(lead) == 100


def test_lead_con_web_buen_rating_muchas_resenas():
    lead = {
        "tiene_sitio_web": True,
        "rating": 4.5,
        "cantidad_resenas": 100
    }
    assert calcular_score(lead) == 0


def test_lead_vacio():
    lead = {}
    assert calcular_score(lead) == 70


def test_solo_sin_web():
    lead = {
        "tiene_sitio_web": False,
        "rating": 4.5,
        "cantidad_resenas": 100
    }
    assert calcular_score(lead) == 40


def test_solo_rating_bajo():
    lead = {
        "tiene_sitio_web": True,
        "rating": 3.0,
        "cantidad_resenas": 100
    }
    assert calcular_score(lead) == 30


def test_solo_pocas_resenas():
    lead = {
        "tiene_sitio_web": True,
        "rating": 4.5,
        "cantidad_resenas": 5
    }
    assert calcular_score(lead) == 30


def test_clasificacion_caliente():
    assert clasificar_lead(80) == "caliente"


def test_clasificacion_tibio():
    assert clasificar_lead(50) == "tibio"


def test_clasificacion_frio():
    assert clasificar_lead(20) == "frio"


def test_clasificacion_limite_caliente():
    assert clasificar_lead(70) == "caliente"


def test_clasificacion_limite_tibio():
    assert clasificar_lead(40) == "tibio"


def test_recomendar_sin_web_y_pocas_resenas_solo_pack_desde_cero():
    lead = {"tiene_sitio_web": False, "rating": 5, "cantidad_resenas": 5, "telefono": "600111222"}
    assert recomendar_servicios(lead) == ["Pack presencia digital desde cero"]


def test_recomendar_lead_ideal_no_sugiere_nada():
    lead = {"tiene_sitio_web": True, "rating": 4.5, "cantidad_resenas": 50, "telefono": "600111222"}
    assert recomendar_servicios(lead) == []


def test_recomendar_sin_web_pero_con_resenas_sugiere_diseno_web():
    lead = {"tiene_sitio_web": False, "rating": 4.5, "cantidad_resenas": 50, "telefono": "600111222"}
    assert recomendar_servicios(lead) == ["Diseno y desarrollo web"]


def test_recomendar_rating_bajo_sugiere_gestion_de_reputacion():
    lead = {"tiene_sitio_web": True, "rating": 2.0, "cantidad_resenas": 50, "telefono": "600111222"}
    assert recomendar_servicios(lead) == ["Gestion de reputacion online"]


def test_recomendar_pocas_resenas_con_web_sugiere_seo_local():
    lead = {"tiene_sitio_web": True, "rating": 4.5, "cantidad_resenas": 3, "telefono": "600111222"}
    assert recomendar_servicios(lead) == ["SEO local y visibilidad"]


def test_recomendar_sin_telefono_sugiere_completar_ficha():
    lead = {"tiene_sitio_web": True, "rating": 4.5, "cantidad_resenas": 50}
    assert recomendar_servicios(lead) == ["Ficha de Google Business incompleta"]


def test_recomendar_combina_varias_senales_con_web():
    lead = {"tiene_sitio_web": True, "rating": 2.0, "cantidad_resenas": 3, "telefono": "No disponible"}
    assert recomendar_servicios(lead) == [
        "Gestion de reputacion online",
        "SEO local y visibilidad",
        "Ficha de Google Business incompleta",
    ]
