import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scoring.lead_scorer import calcular_score, clasificar_lead


def test_lead_completo():
    lead = {
        "tiene_sitio_web": True,
        "tiene_redes_sociales": True,
        "tiene_google_business": True,
        "empleados": 10,
        "tiene_reseñas": True
    }
    assert calcular_score(lead) == 100


def test_lead_vacio():
    lead = {}
    assert calcular_score(lead) == 0


def test_clasificacion_caliente():
    assert clasificar_lead(80) == "caliente"


def test_clasificacion_tibio():
    assert clasificar_lead(50) == "tibio"


def test_clasificacion_frio():
    assert clasificar_lead(20) == "frio"

def test_empleados_pequeño():
    lead = {"empleados": 1}
    assert calcular_score(lead) == 5


def test_empleados_mediano():
    lead = {"empleados": 3}
    assert calcular_score(lead) == 15