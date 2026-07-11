from dotenv import load_dotenv
load_dotenv()


def calcular_score(lead):
    score = 0

    if not lead.get("tiene_sitio_web"):
        score += 40

    rating = lead.get("rating", 5)
    if rating < 3.5:
        score += 30

    reseñas = lead.get("cantidad_resenas", 0)
    if reseñas < 10:
        score += 30

    return score


def clasificar_lead(score):
    if score >= 70:
        return "caliente"
    elif score >= 40:
        return "tibio"
    else:
        return "frio"


def recomendar_servicios(lead):
    servicios = []

    tiene_web = lead.get("tiene_sitio_web")
    rating = lead.get("rating", 5)
    resenas = lead.get("cantidad_resenas", 0)
    telefono = lead.get("telefono", "No disponible")

    if not tiene_web and resenas < 10:
        servicios.append("Pack presencia digital desde cero")
    else:
        if not tiene_web:
            servicios.append("Diseno y desarrollo web")
        if rating < 3.5:
            servicios.append("Gestion de reputacion online")
        if resenas < 10:
            servicios.append("SEO local y visibilidad")
        if telefono == "No disponible":
            servicios.append("Ficha de Google Business incompleta")

    return servicios
