import anthropic

MODELO = "claude-haiku-4-5"
MAX_TOKENS_WHATSAPP = 300
MAX_TOKENS_EMAIL = 600

NOMBRES_SENALES = {
    "formulario_contacto": "formulario de contacto",
    "email_visible": "email visible",
    "whatsapp": "enlace a WhatsApp",
    "https": "HTTPS",
    "favicon": "favicon",
}


def _construir_prompt(datos_lead, formato):
    """Función pura, sin red: arma el texto del prompt a partir de los
    datos del lead. Testeable de forma aislada."""
    nombre = datos_lead.get("nombre", "el negocio")
    categoria = datos_lead.get("categoria")
    visibilidad = datos_lead.get("visibilidad")
    clasificacion = datos_lead.get("clasificacion")
    tiene_web = datos_lead.get("tiene_web")
    senales_oportunidad = datos_lead.get("senales_oportunidad")
    servicios = datos_lead.get("servicios") or []

    contexto = [f"Nombre del negocio: {nombre}"]
    if categoria:
        contexto.append(f"Categoría: {categoria}")
    if visibilidad is not None:
        contexto.append(
            f"Visibilidad (0-100, más alto = más necesidad de mejorar su presencia digital): {visibilidad}"
        )
    if clasificacion:
        contexto.append(f"Clasificación del lead: {clasificacion}")
    contexto.append(f"¿Tiene sitio web?: {'sí' if tiene_web else 'no'}")
    if senales_oportunidad:
        faltantes = [NOMBRES_SENALES.get(k, k) for k, v in senales_oportunidad.items() if not v]
        if faltantes:
            contexto.append(f"Señales que le faltan a su web: {', '.join(faltantes)}")
    if servicios:
        contexto.append(f"Servicios recomendados para este negocio: {', '.join(servicios)}")

    datos_texto = "\n".join(f"- {linea}" for linea in contexto)

    if formato == "email":
        instrucciones_formato = (
            "Escribí un email más desarrollado, con saludo inicial y despedida, "
            "de no más de 150 palabras."
        )
    else:
        instrucciones_formato = (
            "Escribí un mensaje breve para WhatsApp (2 a 4 oraciones cortas, sin asunto, "
            "como si lo tipearas vos mismo desde el celular)."
        )

    return f"""Sos un consultor de marketing digital que está por contactar a un negocio real luego de auditarlo.

Datos de la auditoría:
{datos_texto}

Redactá un mensaje para contactar a este negocio con estas reglas:
- Mencioná el nombre del negocio.
- Apoyate en los datos reales de arriba (no inventes cifras, calificaciones ni datos que no estén en la lista).
- Sugerí solo los servicios que este negocio necesita según los datos — no ofrezcas de más.
- Tono profesional, cercano y consultivo. Nada de spam ni de lenguaje de venta agresivo.
- No prometas resultados concretos ni des precios.
- Terminá invitando a conversar (una llamada, una reunión breve, o simplemente charlar).
{instrucciones_formato}

Devolvé SOLO el texto del mensaje, sin explicaciones ni comillas."""


def generar_propuesta(datos_lead, formato="whatsapp"):
    """Función aislada, sin dependencias de Flask: genera una propuesta
    comercial personalizada con Claude. Devuelve {"ok": True, "texto": ...}
    o {"ok": False, "error": "..."} — nunca deja subir la excepción."""
    prompt = _construir_prompt(datos_lead, formato)
    max_tokens = MAX_TOKENS_EMAIL if formato == "email" else MAX_TOKENS_WHATSAPP
    try:
        cliente = anthropic.Anthropic()
        respuesta = cliente.messages.create(
            model=MODELO,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        texto = next((b.text for b in respuesta.content if b.type == "text"), "").strip()
        if not texto:
            return {"ok": False, "error": "No se pudo generar la propuesta. Probá de nuevo."}
        return {"ok": True, "texto": texto}
    except anthropic.AuthenticationError:
        return {"ok": False, "error": "Error de configuración: la clave de la API de IA no es válida."}
    except anthropic.RateLimitError:
        return {"ok": False, "error": "El servicio de IA está saturado. Probá de nuevo en unos segundos."}
    except anthropic.APIConnectionError:
        return {"ok": False, "error": "No se pudo conectar con el servicio de IA."}
    except anthropic.APIStatusError:
        return {"ok": False, "error": "El servicio de IA no pudo procesar la solicitud."}
    except Exception:
        return {"ok": False, "error": "No se pudo generar la propuesta. Probá de nuevo."}
