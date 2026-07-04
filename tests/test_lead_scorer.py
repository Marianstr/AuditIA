import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scoring.lead_scorer import calcular_score, clasificar_lead


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
