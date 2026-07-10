import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scoring.analizador_web import analizar_senales


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
