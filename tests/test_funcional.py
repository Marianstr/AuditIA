import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scoring.lead_scorer import calcular_score, clasificar_lead


def test_flujo_lead_sin_presencia_digital():
    """Un negocio sin nada online debe ser frío pero con mucho potencial"""
    lead = {
        "tiene_sitio_web": False,
        "tiene_redes_sociales": False,
        "tiene_google_business": False,
        "empleados": 5,
        "tiene_reseñas": False
    }
    score = calcular_score(lead)
    clasificacion = clasificar_lead(score)
    assert score == 15
    assert clasificacion == "frio"


def test_flujo_lead_presencia_parcial():
    """Un negocio con sitio web pero sin redes es tibio"""
    lead = {
        "tiene_sitio_web": True,
        "tiene_redes_sociales": False,
        "tiene_google_business": True,
        "empleados": 3,
        "tiene_reseñas": False
    }
    score = calcular_score(lead)
    clasificacion = clasificar_lead(score)
    assert score == 50
    assert clasificacion == "tibio"


def test_flujo_lead_ideal_para_auditia():
    """Un negocio mediano sin presencia digital es el cliente ideal"""
    lead = {
        "tiene_sitio_web": False,
        "tiene_redes_sociales": False,
        "tiene_google_business": False,
        "empleados": 10,
        "tiene_reseñas": False
    }
    score = calcular_score(lead)
    clasificacion = clasificar_lead(score)
    assert score == 25
    assert clasificacion == "frio"