def calcular_score(lead):
    score = 0

    # Tiene sitio web?
    if lead.get("tiene_sitio_web"):
        score += 20

    # Tiene redes sociales?
    if lead.get("tiene_redes_sociales"):
        score += 15

    # Tiene Google My Business?
    if lead.get("tiene_google_business"):
        score += 15

    # Cuántos empleados tiene?
    empleados = lead.get("empleados", 0)
    if empleados >= 10:
        score += 25
    elif empleados >= 3:
        score += 15
    elif empleados >= 1:
        score += 5

    # Tiene reseñas online?
    if lead.get("tiene_reseñas"):
        score += 25

    return score


def clasificar_lead(score):
    if score >= 70:
        return "caliente"
    elif score >= 40:
        return "tibio"
    else:
        return "frio"