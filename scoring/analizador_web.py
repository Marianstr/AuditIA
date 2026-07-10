import re
from urllib.parse import urlsplit

import requests
from bs4 import BeautifulSoup

TIMEOUT_PAGINA = 5
TIMEOUT_FAVICON = 3
USER_AGENT = "Mozilla/5.0 (compatible; AuditIA/1.0)"

EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")


def obtener_html(url, timeout=TIMEOUT_PAGINA):
    """Descarga una página. Devuelve (html, url_final, error).
    Si falla, html y url_final son None y error trae un mensaje legible."""
    try:
        respuesta = requests.get(
            url,
            timeout=timeout,
            headers={"User-Agent": USER_AGENT},
            allow_redirects=True
        )
        respuesta.raise_for_status()
        return respuesta.text, respuesta.url, None
    except requests.exceptions.Timeout:
        return None, None, "La web tardó demasiado en responder."
    except requests.exceptions.SSLError:
        return None, None, "La web tiene un certificado de seguridad inválido."
    except requests.exceptions.ConnectionError:
        return None, None, "No se pudo conectar con la web."
    except requests.exceptions.HTTPError as e:
        return None, None, f"La web respondió con un error ({e.response.status_code})."
    except requests.exceptions.RequestException:
        return None, None, "No se pudo analizar la web."


def _tiene_favicon_declarado(soup):
    for link in soup.find_all("link"):
        rel = link.get("rel", [])
        if isinstance(rel, str):
            rel = [rel]
        if "icon" in " ".join(rel).lower() and link.get("href"):
            return True
    return False


def _tiene_favicon_por_defecto(url_final, timeout=TIMEOUT_FAVICON):
    try:
        partes = urlsplit(url_final)
        base = f"{partes.scheme}://{partes.netloc}"
        resp = requests.head(base + "/favicon.ico", timeout=timeout, headers={"User-Agent": USER_AGENT})
        return resp.status_code == 200
    except requests.exceptions.RequestException:
        return False


def analizar_senales(html, url_final, favicon_por_defecto=False):
    """Función pura, sin red: recibe el HTML ya descargado, la URL final
    (post-redirects) y si se detectó un favicon por defecto en /favicon.ico
    (ese chequeo se hace afuera, en analizar_web, porque implica red).
    Devuelve las 5 señales + el conteo."""
    soup = BeautifulSoup(html, "html.parser")
    texto = soup.get_text(" ", strip=True)

    tiene_formulario = soup.find("form") is not None

    tiene_email = bool(soup.select_one('a[href^="mailto:"]')) or bool(EMAIL_REGEX.search(texto))

    tiene_whatsapp = any(
        "wa.me" in (a.get("href") or "") or "api.whatsapp.com" in (a.get("href") or "")
        for a in soup.find_all("a")
    )

    tiene_https = url_final.startswith("https://")

    tiene_favicon = _tiene_favicon_declarado(soup) or favicon_por_defecto

    señales = {
        "formulario_contacto": tiene_formulario,
        "email_visible": tiene_email,
        "whatsapp": tiene_whatsapp,
        "https": tiene_https,
        "favicon": tiene_favicon,
    }
    presentes = sum(señales.values())
    faltantes = 5 - presentes

    return {
        "señales": señales,
        "señales_presentes": presentes,
        "señales_faltantes": faltantes,
        "oportunidad_web": round((faltantes / 5) * 100),
    }


def analizar_web(url, timeout=TIMEOUT_PAGINA):
    """Función pública y aislada: recibe la URL, descarga la página y
    devuelve el análisis completo. No depende de Flask ni de ningún otro
    módulo de la app."""
    html, url_final, error = obtener_html(url, timeout=timeout)
    if error:
        return {"ok": False, "error": error}
    soup = BeautifulSoup(html, "html.parser")
    favicon_por_defecto = False if _tiene_favicon_declarado(soup) else _tiene_favicon_por_defecto(url_final)
    resultado = analizar_senales(html, url_final, favicon_por_defecto=favicon_por_defecto)
    resultado["ok"] = True
    return resultado
