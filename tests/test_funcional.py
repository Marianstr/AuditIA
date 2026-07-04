import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scoring.lead_scorer import calcular_score, clasificar_lead


def test_flujo_lead_sin_presencia_digital():
    lead = {
        "tiene_sitio_web": False,
        "rating": 3.0,
        "cantidad_resenas": 5
    }
    score = calcular_score(lead)
    clasificacion = clasificar_lead(score)
    assert score == 100
    assert clasificacion == "caliente"


def test_flujo_lead_presencia_parcial():
    lead = {
        "tiene_sitio_web": True,
        "rating": 3.0,
        "cantidad_resenas": 100
    }
    score = calcular_score(lead)
    clasificacion = clasificar_lead(score)
    assert score == 30
    assert clasificacion == "frio"


def test_flujo_lead_ideal_para_auditia():
    lead = {
        "tiene_sitio_web": False,
        "rating": 4.5,
        "cantidad_resenas": 100
    }
    score = calcular_score(lead)
    clasificacion = clasificar_lead(score)
    assert score == 40
    assert clasificacion == "tibio"
