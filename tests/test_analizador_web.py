import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from unittest.mock import patch, MagicMock

import requests

from scoring.analizador_web import analizar_senales, obtener_html, analizar_web


def test_web_completa_tiene_las_5_senales():
    html = """
    <html><head><link rel="icon" href="/favicon.ico"></head>
    <body>
        <form><input type="email"></form>
        <a href="mailto:hola@negocio.com">Escribinos</a>
        <a href="https://wa.me/34600000000">WhatsApp</a>
    </body></html>
    """
    resultado = analizar_senales(html, "https://negocio.com")
    assert resultado["señales"] == {
        "formulario_contacto": True,
        "email_visible": True,
        "whatsapp": True,
        "https": True,
        "favicon": True,
    }
    assert resultado["señales_presentes"] == 5
    assert resultado["señales_faltantes"] == 0
    assert resultado["oportunidad_web"] == 0


def test_web_vacia_no_tiene_ninguna_senal():
    html = "<html><head></head><body><p>Sin nada relevante.</p></body></html>"
    resultado = analizar_senales(html, "http://negocio.com")
    assert resultado["señales"] == {
        "formulario_contacto": False,
        "email_visible": False,
        "whatsapp": False,
        "https": False,
        "favicon": False,
    }
    assert resultado["señales_presentes"] == 0
    assert resultado["señales_faltantes"] == 5
    assert resultado["oportunidad_web"] == 100


def test_email_detectado_en_texto_visible_sin_mailto():
    html = "<html><body><p>Escribinos a hola@negocio.com</p></body></html>"
    resultado = analizar_senales(html, "http://negocio.com")
    assert resultado["señales"]["email_visible"] is True


def test_favicon_por_defecto_pasado_como_parametro():
    html = "<html><head></head><body></body></html>"
    resultado = analizar_senales(html, "https://negocio.com", favicon_por_defecto=True)
    assert resultado["señales"]["favicon"] is True


def test_https_segun_url_final():
    html = "<html><body></body></html>"
    resultado = analizar_senales(html, "http://negocio.com")
    assert resultado["señales"]["https"] is False
    resultado = analizar_senales(html, "https://negocio.com")
    assert resultado["señales"]["https"] is True


def test_oportunidad_web_con_tres_senales_presentes():
    html = """
    <html><head><link rel="icon" href="/favicon.ico"></head>
    <body><a href="mailto:hola@negocio.com">Email</a></body></html>
    """
    # favicon + email + https (por la URL) = 3 de 5
    resultado = analizar_senales(html, "https://negocio.com")
    assert resultado["señales_presentes"] == 3
    assert resultado["señales_faltantes"] == 2
    assert resultado["oportunidad_web"] == 40


# ---------- obtener_html() — con requests.get mockeado, sin red real ----------

def test_obtener_html_exito():
    mock_resp = MagicMock()
    mock_resp.text = "<html>ok</html>"
    mock_resp.url = "https://negocio.com/"
    mock_resp.raise_for_status.return_value = None
    with patch("scoring.analizador_web.requests.get", return_value=mock_resp) as mock_get:
        html, url_final, error = obtener_html("https://negocio.com")

    assert html == "<html>ok</html>"
    assert url_final == "https://negocio.com/"
    assert error is None
    mock_get.assert_called_once()


def test_obtener_html_timeout():
    with patch("scoring.analizador_web.requests.get", side_effect=requests.exceptions.Timeout):
        html, url_final, error = obtener_html("https://negocio.com")

    assert html is None
    assert url_final is None
    assert error == "La web tardó demasiado en responder."


def test_obtener_html_connection_error():
    with patch("scoring.analizador_web.requests.get", side_effect=requests.exceptions.ConnectionError):
        html, url_final, error = obtener_html("https://negocio.com")

    assert html is None
    assert error == "No se pudo conectar con la web."


def test_obtener_html_ssl_error():
    with patch("scoring.analizador_web.requests.get", side_effect=requests.exceptions.SSLError):
        html, url_final, error = obtener_html("https://negocio.com")

    assert error == "La web tiene un certificado de seguridad inválido."


def test_obtener_html_http_error():
    mock_resp = MagicMock()
    error_http = requests.exceptions.HTTPError(response=MagicMock(status_code=404))
    mock_resp.raise_for_status.side_effect = error_http
    with patch("scoring.analizador_web.requests.get", return_value=mock_resp):
        html, url_final, error = obtener_html("https://negocio.com")

    assert error == "La web respondió con un error (404)."


def test_obtener_html_request_exception_generico():
    with patch("scoring.analizador_web.requests.get", side_effect=requests.exceptions.RequestException):
        html, url_final, error = obtener_html("https://negocio.com")

    assert error == "No se pudo analizar la web."


# ---------- analizar_web() — orquestador, con requests mockeado ----------

def _mock_get_html(html, url_final="https://negocio.com/"):
    mock_resp = MagicMock()
    mock_resp.text = html
    mock_resp.url = url_final
    mock_resp.raise_for_status.return_value = None
    return mock_resp


def test_analizar_web_exito_favicon_por_defecto():
    html = """
    <html><body>
        <form><input type="email"></form>
        <a href="mailto:hola@negocio.com">Escribinos</a>
        <a href="https://wa.me/34600000000">WhatsApp</a>
    </body></html>
    """
    mock_head_resp = MagicMock(status_code=200)
    with patch("scoring.analizador_web.requests.get", return_value=_mock_get_html(html)), \
         patch("scoring.analizador_web.requests.head", return_value=mock_head_resp) as mock_head:
        resultado = analizar_web("https://negocio.com")

    assert resultado["ok"] is True
    assert resultado["señales"]["favicon"] is True
    assert resultado["señales_presentes"] == 5
    mock_head.assert_called_once()


def test_analizar_web_favicon_declarado_no_llama_head():
    html = '<html><head><link rel="icon" href="/favicon.ico"></head><body></body></html>'
    with patch("scoring.analizador_web.requests.get", return_value=_mock_get_html(html)), \
         patch("scoring.analizador_web.requests.head") as mock_head:
        resultado = analizar_web("https://negocio.com")

    assert resultado["ok"] is True
    assert resultado["señales"]["favicon"] is True
    mock_head.assert_not_called()


def test_analizar_web_timeout_devuelve_error_sin_llamar_head():
    with patch("scoring.analizador_web.requests.get", side_effect=requests.exceptions.Timeout), \
         patch("scoring.analizador_web.requests.head") as mock_head:
        resultado = analizar_web("https://negocio.com")

    assert resultado == {"ok": False, "error": "La web tardó demasiado en responder."}
    mock_head.assert_not_called()


def test_analizar_web_connection_error_devuelve_error():
    with patch("scoring.analizador_web.requests.get", side_effect=requests.exceptions.ConnectionError):
        resultado = analizar_web("https://negocio.com")

    assert resultado == {"ok": False, "error": "No se pudo conectar con la web."}


def test_analizar_web_falla_chequeo_de_favicon_por_defecto():
    html = "<html><body>Sin favicon declarado</body></html>"
    with patch("scoring.analizador_web.requests.get", return_value=_mock_get_html(html)), \
         patch("scoring.analizador_web.requests.head", side_effect=requests.exceptions.ConnectionError):
        resultado = analizar_web("https://negocio.com")

    assert resultado["ok"] is True
    assert resultado["señales"]["favicon"] is False
