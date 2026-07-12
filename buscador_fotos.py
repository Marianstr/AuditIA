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


def termino_busqueda(categoria):
    """Convierte una categoría en español al mejor término de búsqueda en inglés."""
    if not categoria:
        return TERMINO_POR_DEFECTO
    norm = _normalizar(categoria)
    if norm in TRADUCCIONES:
        return TRADUCCIONES[norm]
    # Coincidencia parcial: si la categoría contiene una palabra conocida.
    for clave, valor in TRADUCCIONES.items():
        if clave in norm:
            return valor
    # Red de seguridad: término genérico lindo (evita fotos random).
    return TERMINO_POR_DEFECTO


def buscar_foto_categoria(categoria):
    """Busca una foto de la categoría en Pexels. Devuelve la URL de la imagen,
    o None si algo falla (red de seguridad para no romper el mockup)."""
    try:
        api_key = os.environ.get("PEXELS_API_KEY")
        if not api_key:
            return None
        query = termino_busqueda(categoria)
        resp = requests.get(
            "https://api.pexels.com/v1/search",
            headers={"Authorization": api_key},
            params={"query": query, "per_page": 1, "orientation": "landscape"},
            timeout=8,
        )
        if resp.status_code != 200:
            return None
        fotos = resp.json().get("photos", [])
        if not fotos:
            return None
        return fotos[0]["src"]["large"]
    except Exception:
        return None
