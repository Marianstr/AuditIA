import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from unittest.mock import patch, MagicMock
import anthropic
import generador_propuesta as gp


def test_prompt_incluye_nombre_categoria_y_servicios():
    datos = {
        "nombre": "Panadería López",
        "categoria": "panaderías",
        "visibilidad": 70,
        "clasificacion": "caliente",
        "tiene_web": False,
        "senales_oportunidad": None,
        "servicios": ["Diseño y desarrollo web"],
    }
    prompt = gp._construir_prompt(datos, "whatsapp")
    assert "Panadería López" in prompt
    assert "panaderías" in prompt
    assert "caliente" in prompt
    assert "Diseño y desarrollo web" in prompt


def test_prompt_indica_si_no_tiene_web():
    datos = {"nombre": "X", "tiene_web": False}
    prompt = gp._construir_prompt(datos, "whatsapp")
    assert "¿Tiene sitio web?: no" in prompt


def test_prompt_incluye_senales_faltantes():
    datos = {
        "nombre": "X",
        "tiene_web": True,
        "senales_oportunidad": {
            "formulario_contacto": False,
            "email_visible": False,
            "whatsapp": True,
            "https": True,
            "favicon": True,
        },
    }
    prompt = gp._construir_prompt(datos, "whatsapp")
    assert "formulario de contacto" in prompt
    assert "email visible" in prompt
    # las que sí tiene no deberían aparecer como faltantes
    assert "Señales que le faltan a su web: formulario de contacto, email visible" in prompt


def test_prompt_sin_senales_faltantes_no_menciona_la_linea():
    datos = {
        "nombre": "X",
        "tiene_web": True,
        "senales_oportunidad": {
            "formulario_contacto": True,
            "email_visible": True,
            "whatsapp": True,
            "https": True,
            "favicon": True,
        },
    }
    prompt = gp._construir_prompt(datos, "whatsapp")
    assert "Señales que le faltan" not in prompt


def test_prompt_formato_whatsapp_vs_email_difiere():
    datos = {"nombre": "X", "tiene_web": True}
    prompt_wa = gp._construir_prompt(datos, "whatsapp")
    prompt_email = gp._construir_prompt(datos, "email")
    assert prompt_wa != prompt_email
    assert "WhatsApp" in prompt_wa
    assert "email" in prompt_email.lower()


def test_generar_propuesta_maneja_error_de_conexion_sin_llamar_api_real():
    datos = {"nombre": "X", "tiene_web": True}
    with patch("generador_propuesta.anthropic.Anthropic") as ClienteMock:
        instancia = ClienteMock.return_value
        instancia.messages.create.side_effect = anthropic.APIConnectionError(request=MagicMock())
        resultado = gp.generar_propuesta(datos, "whatsapp")
    assert resultado == {"ok": False, "error": "No se pudo conectar con el servicio de IA."}
    instancia.messages.create.assert_called_once()


def test_generar_propuesta_exito_con_mock():
    datos = {"nombre": "X", "tiene_web": True}
    bloque_texto = MagicMock()
    bloque_texto.type = "text"
    bloque_texto.text = "Hola, te escribo porque..."
    respuesta_mock = MagicMock()
    respuesta_mock.content = [bloque_texto]
    with patch("generador_propuesta.anthropic.Anthropic") as ClienteMock:
        ClienteMock.return_value.messages.create.return_value = respuesta_mock
        resultado = gp.generar_propuesta(datos, "whatsapp")
    assert resultado == {"ok": True, "texto": "Hola, te escribo porque..."}
