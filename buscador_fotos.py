import os
import unicodedata
import requests

# Diccionario de categorías comunes (español) -> término de búsqueda en inglés.
# Pexels tiene muchas más fotos, y mejor etiquetadas, en inglés.
TRADUCCIONES = {
    "floristeria": "flower shop", "floristerias": "flower shop", "florista": "flower shop",
    "peluqueria": "hair salon", "peluquerias": "hair salon", "barberia": "barber shop",
    "restaurante": "restaurant interior", "restaurantes": "restaurant interior",
    "cafeteria": "coffee shop", "cafeterias": "coffee shop", "bar": "bar interior",
    "panaderia": "bakery", "pasteleria": "pastry shop", "heladeria": "ice cream shop",
    "fotografia": "photography studio", "fotografo": "photography studio",
    "fotografos": "photography studio", "casa de fotografia": "photography studio",
    "estudio fotografico": "photography studio",
    "gimnasio": "modern gym", "gimnasios": "modern gym",
    "clinica dental": "dental clinic", "dentista": "dental clinic", "dentistas": "dental clinic",
    "veterinaria": "veterinary clinic", "veterinario": "veterinary clinic",
    "abogado": "law office", "abogados": "law office", "estudio juridico": "law office",
    "inmobiliaria": "real estate office", "inmobiliarias": "modern real estate",
    "tienda de ropa": "clothing boutique", "boutique": "clothing boutique", "moda": "fashion boutique",
    "zapateria": "shoe store", "joyeria": "jewelry store",
    "libreria": "bookstore", "jugueteria": "toy store", "ferreteria": "hardware store",
    "supermercado": "grocery store", "farmacia": "pharmacy",
    "hotel": "hotel lobby", "hoteles": "boutique hotel", "spa": "luxury spa",
    "estetica": "beauty salon", "centro de estetica": "beauty salon",
    "taller mecanico": "auto repair shop", "mecanico": "auto repair shop",
    "carpinteria": "carpentry workshop", "electricista": "electrician",
    "arquitecto": "architecture studio", "diseno": "design studio", "agencia": "creative agency",
    "consultora": "modern office", "contador": "accounting office",
    "verduleria": "greengrocer", "carniceria": "butcher shop", "pescaderia": "fish market",
    "vinoteca": "wine shop", "cerveceria": "brewery", "pizzeria": "pizzeria",
}

TERMINO_POR_DEFECTO = "modern business storefront"


def _normalizar(texto):
    texto = texto.lower().strip()
    texto = "".join(
        c for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    )
    return texto


def termino_busqueda(categoria, ya_en_ingles=False):
    """Convierte una categoría en español al mejor término de búsqueda en inglés.
    Si ya_en_ingles=True (por ejemplo, un término elegido por la IA), se devuelve
    la categoría tal cual, sin pasar por el diccionario de traducciones."""
    if not categoria:
        return TERMINO_POR_DEFECTO
    if ya_en_ingles:
        return categoria
    norm = _normalizar(categoria)
    if norm in TRADUCCIONES:
        return TRADUCCIONES[norm]
    # Coincidencia parcial: si la categoría contiene una palabra conocida.
    for clave, valor in TRADUCCIONES.items():
        if clave in norm:
            return valor
    # Red de seguridad: término genérico lindo (evita fotos random).
    return TERMINO_POR_DEFECTO


def buscar_fotos_categoria(categoria, cantidad=None, ya_en_ingles=False):
    """Busca fotos de calidad de la categoría en Pexels. Devuelve URLs distintas,
    descartando fotos pequeñas o demasiado cuadradas. Si `cantidad` es None,
    devuelve todas las que pasan el filtro (hasta las 15 que pide a Pexels).
    Devuelve lista vacía si algo falla (red de seguridad para no romper el mockup)."""
    try:
        api_key = os.environ.get("PEXELS_API_KEY")
        if not api_key:
            return []
        query = termino_busqueda(categoria, ya_en_ingles=ya_en_ingles)
        resp = requests.get(
            "https://api.pexels.com/v1/search",
            headers={"Authorization": api_key},
            params={"query": query, "per_page": 15, "orientation": "landscape"},
            timeout=8,
        )
        if resp.status_code != 200:
            return []
        fotos = resp.json().get("photos", [])
        urls = []
        vistas = set()
        for foto in fotos:
            ancho = foto.get("width") or 0
            alto = foto.get("height") or 0
            if ancho < 1200 or alto <= 0:
                continue
            if (ancho / alto) < 1.2:
                continue
            url = foto.get("src", {}).get("large")
            if not url or url in vistas:
                continue
            vistas.add(url)
            urls.append(url)
            if cantidad is not None and len(urls) >= cantidad:
                break
        return urls
    except Exception:
        return []


def buscar_foto_categoria(categoria):
    """Busca una foto de la categoría en Pexels. Devuelve la URL de la imagen,
    o None si algo falla (red de seguridad para no romper el mockup)."""
    fotos = buscar_fotos_categoria(categoria, cantidad=1)
    return fotos[0] if fotos else None
