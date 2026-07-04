def calcular_score(lead):
    score = 0

    # No tiene sitio web = buen lead
    if not lead.get("tiene_sitio_web"):
        score += 40

    # Rating bajo = presencia débil
    rating = lead.get("rating", 5)
    if rating < 3.5:
        score += 30

    # Pocas reseñas = poca visibilidad
    reseñas = lead.get("cantidad_reseñas", 0)
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

