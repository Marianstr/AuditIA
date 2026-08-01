import json
import re
from datetime import datetime

import anthropic

from presets import listar_presets

MODELO = "claude-haiku-4-5"
MAX_TOKENS = 3000

MAX_PALABRAS_RUBRO = 5
MAX_CARACTERES_RUBRO = 60

CANTIDAD_HERO_TITULO = 3
CANTIDAD_HERO_TAGS = 3
CANTIDAD_VENTAJAS = 4
CANTIDAD_SERVICIOS = 3
CANTIDAD_PASOS = 4
CANTIDAD_FOOTER_COLUMNAS = 3


def _describir_presets():
    return "\n".join(
        f'- id: "{p["id"]}" | {p["nombre"]}: {p["descripcion"]} Ejemplos: {p["ejemplos"]}'
        for p in listar_presets()
    )


def _construir_prompt(lead):
    nombre = lead.get("nombre") or "el negocio"
    direccion = lead.get("direccion") or ""
    telefono = lead.get("telefono") or ""
    web = lead.get("web") or ""
    rating = lead.get("rating")
    cantidad_resenas = lead.get("cantidad_resenas")
    score = lead.get("score")
    clasificacion = lead.get("clasificacion") or ""
    servicios = lead.get("servicios") or []
    primary_type = lead.get("primary_type") or ""
    categoria_google = lead.get("categoria_google") or ""
    tipos = lead.get("tipos") or []

    contexto = [f"Nombre del negocio: {nombre}"]
    if direccion:
        contexto.append(f"Dirección: {direccion}")
    if telefono:
        contexto.append(f"Teléfono: {telefono}")
    if web:
        contexto.append(f"Web actual: {web}")
    if rating is not None:
        contexto.append(f"Valoración en Google: {rating}")
    if cantidad_resenas is not None:
        contexto.append(f"Cantidad de reseñas: {cantidad_resenas}")
    if score is not None:
        contexto.append(f"Score de oportunidad (0-100, más alto = más necesidad de mejorar su presencia digital): {score}")
    if clasificacion:
        contexto.append(f"Clasificación del lead: {clasificacion}")
    if primary_type:
        contexto.append(f"Categoría principal (Google): {primary_type}")
    if categoria_google:
        contexto.append(f"Categoría Google: {categoria_google}")
    if tipos:
        contexto.append(f"Tipos asociados: {', '.join(tipos)}")
    if servicios:
        contexto.append(f"Servicios recomendados para este negocio: {', '.join(servicios)}")

    datos_texto = "\n".join(f"- {linea}" for linea in contexto)

    return f"""Sos un copywriter que redacta el contenido de una landing page de demostración para un negocio real, como parte de una propuesta comercial de una agencia de marketing digital.

Datos del negocio:
{datos_texto}

Elegí el preset visual más adecuado para este negocio entre estos (usá el "id" exacto tal cual aparece):
{_describir_presets()}

Devolvé SOLO un JSON válido, sin backticks, sin markdown y sin texto antes ni después, con esta forma EXACTA (mismas claves, mismos tipos):

{{
  "preset": "<id de preset>",
  "rubro": "<tipo de negocio o especialidad, sin ciudad ni barrio>",
  "hero_titulo": ["línea 1", "línea 2", "línea 3"],
  "hero_sub": "...",
  "cta_1": "...", "cta_2": "...", "nav_boton": "...", "cta_servicio": "...",
  "hero_tags": ["...", "...", "..."],
  "nav": [{{"texto": "...", "ancla": "#servicios"}}],
  "ventajas": [{{"titulo": "...", "texto": "..."}}],
  "servicios_kicker": "...", "servicios_titulo": "...", "servicios_intro": "...",
  "servicios": [{{"nombre": "...", "dato_1": "...", "dato_2": "...", "etiqueta": null}}],
  "metodo_kicker": "...", "metodo_titulo": "...", "metodo_intro": "...",
  "pasos": [{{"titulo": "...", "texto": "..."}}],
  "contacto_kicker": "...", "contacto_titulo": "...",
  "etq_direccion": "...", "etq_horario": "...", "etq_telefono": "...", "etq_email": "...",
  "footer_texto": "...",
  "footer_columnas": [{{"titulo": "...", "enlaces": [{{"texto": "...", "ancla": "#..."}}]}}],
  "news_titulo": "...", "news_texto": "...", "news_boton": "..."
}}

Reglas obligatorias:
- Escribí todo el texto en español de España.
- "rubro" tiene que ser una etiqueta corta de máximo 5 palabras que describa el TIPO de negocio o su especialidad, tipo "Peluquería y estética", "Taller mecánico multimarca", "Clínica dental familiar" o "Panadería artesana". No menciones ciudad, barrio ni dirección: esa información ya aparece en la sección de contacto. Nunca una frase larga ni con punto final.
- "hero_titulo" tiene que tener exactamente 3 líneas y "hero_tags" exactamente 3 etiquetas.
- "ventajas" tiene que tener exactamente 4 elementos, "servicios" exactamente 3, "pasos" exactamente 4 y "footer_columnas" exactamente 3 (cada columna con al menos un enlace).
- No inventes precios, testimonios, datos de contacto, estadísticas, años de fundación ni número de clientes. Si no tenés un dato real, no lo menciones.
- El "preset" tiene que ser uno de los ids de la lista de arriba, el que mejor encaje con el rubro del negocio.
- Los textos tienen que ser concretos y creíbles para este negocio en particular, no genéricos de relleno.
- Los campos "ancla" tienen que ser anclas internas de la propia página (empiezan con "#"), por ejemplo #servicios, #metodologia, #contacto.
- El campo "etiqueta" de cada servicio va en null salvo que tengas una razón real para destacarlo (no inventes ofertas).
- "nav_boton" tiene que ser una llamada a la acción, tipo "Pedir cita", "Llamar ahora" o "Pedir presupuesto". Nunca puede repetir el texto de ninguno de los enlaces de "nav"."""


def _limitar_rubro(texto):
    """Recorta "rubro" a máximo 5 palabras y 60 caracteres, sin punto final."""
    texto = (texto or "").strip().rstrip(".")
    texto = " ".join(texto.split()[:MAX_PALABRAS_RUBRO])
    return texto[:MAX_CARACTERES_RUBRO].strip()


def _limpiar_json(texto):
    texto = texto.strip()
    texto = re.sub(r"^```(?:json)?\s*", "", texto)
    texto = re.sub(r"\s*```$", "", texto)
    return texto.strip()


def _es_valido(contenido):
    if not isinstance(contenido, dict):
        return False
    listas_con_largo_minimo = {
        "hero_titulo": CANTIDAD_HERO_TITULO,
        "hero_tags": CANTIDAD_HERO_TAGS,
        "ventajas": CANTIDAD_VENTAJAS,
        "servicios": CANTIDAD_SERVICIOS,
        "pasos": CANTIDAD_PASOS,
        "footer_columnas": CANTIDAD_FOOTER_COLUMNAS,
    }
    for clave, largo_minimo in listas_con_largo_minimo.items():
        valor = contenido.get(clave)
        if not isinstance(valor, list) or len(valor) < largo_minimo:
            return False
    if not isinstance(contenido.get("nav"), list) or not contenido["nav"]:
        return False
    ids_validos = {p["id"] for p in listar_presets()}
    if contenido.get("preset") not in ids_validos:
        return False
    return True


def _contenido_de_reserva(lead):
    """Contenido de reserva, siempre válido para la plantilla, usado si
    la IA falla o devuelve algo con una forma inesperada."""
    nombre = lead.get("nombre") or "Tu negocio"
    rubro = lead.get("primary_type") or lead.get("categoria_google") or "tu negocio"
    return {
        "preset": "corporativo_sobrio",
        "rubro": _limitar_rubro(rubro),
        "hero_titulo": [nombre, "en internet,", "de forma profesional"],
        "hero_sub": f"Así podría verse la presencia online de {nombre}.",
        "cta_1": "Ver servicios",
        "cta_2": "Cómo trabajamos",
        "nav_boton": "Pedir cita",
        "cta_servicio": "Más información",
        "hero_tags": ["Atención cercana", "Presencia digital", "Fácil de contactar"],
        "nav": [
            {"texto": "Servicios", "ancla": "#servicios"},
            {"texto": "Cómo trabajamos", "ancla": "#metodologia"},
            {"texto": "Contacto", "ancla": "#contacto"},
        ],
        "ventajas": [
            {"titulo": "Atención cercana", "texto": "Un trato directo y personalizado en cada consulta."},
            {"titulo": "Presencia digital", "texto": "Una web pensada para que os encuentren con facilidad."},
            {"titulo": "Fácil de contactar", "texto": "Todos los datos de contacto a un clic de distancia."},
            {"titulo": "Información clara", "texto": "Todo lo que necesitáis saber, sin vueltas."},
        ],
        "servicios_kicker": "Servicios",
        "servicios_titulo": "Lo que ofrecemos",
        "servicios_intro": "Un resumen de nuestra actividad.",
        "servicios": [
            {"nombre": "Servicio principal", "dato_1": "", "dato_2": "", "etiqueta": None},
            {"nombre": "Servicio adicional", "dato_1": "", "dato_2": "", "etiqueta": None},
            {"nombre": "Atención personalizada", "dato_1": "", "dato_2": "", "etiqueta": None},
        ],
        "metodo_kicker": "Cómo trabajamos",
        "metodo_titulo": "Nuestro método",
        "metodo_intro": "Un proceso simple y claro.",
        "pasos": [
            {"titulo": "Contacto", "texto": "Os ponéis en contacto con nosotros."},
            {"titulo": "Consulta", "texto": "Analizamos juntos qué necesitáis."},
            {"titulo": "Propuesta", "texto": "Os presentamos la mejor opción."},
            {"titulo": "Resultado", "texto": "Ponemos manos a la obra."},
        ],
        "contacto_kicker": "Contacto",
        "contacto_titulo": "Hablemos",
        "etq_direccion": "Dirección",
        "etq_horario": "Horario",
        "etq_telefono": "Teléfono",
        "etq_email": "Email",
        "footer_texto": f"{nombre}, cerca de vosotros.",
        "footer_columnas": [
            {"titulo": "Navegación", "enlaces": [{"texto": "Servicios", "ancla": "#servicios"}, {"texto": "Contacto", "ancla": "#contacto"}]},
            {"titulo": "Servicios", "enlaces": [{"texto": "Consultas", "ancla": "#servicios"}]},
            {"titulo": "Contacto", "enlaces": [{"texto": "Cómo llegar", "ancla": "#contacto"}]},
        ],
        "news_titulo": "Mantente al día",
        "news_texto": "Novedades y avisos importantes.",
        "news_boton": "Enviar",
    }


def generar_contenido_landing(lead):
    """Genera el contenido textual de la landing de demostración con Claude.

    Devuelve siempre un dict con la forma que espera mockup_base.html
    (incluidas las claves fijas anio/promo/testimonio/destacado). Si la IA
    falla o devuelve algo con forma inesperada, cae a un contenido de
    reserva válido en vez de propagar la excepción."""
    prompt = _construir_prompt(lead)
    contenido = None
    try:
        cliente = anthropic.Anthropic()
        respuesta = cliente.messages.create(
            model=MODELO,
            max_tokens=MAX_TOKENS,
            messages=[{"role": "user", "content": prompt}],
        )
        texto = next((b.text for b in respuesta.content if b.type == "text"), "").strip()
        contenido = json.loads(_limpiar_json(texto))
        if not _es_valido(contenido):
            contenido = None
    except Exception:
        contenido = None

    if contenido is None:
        contenido = _contenido_de_reserva(lead)
    else:
        contenido["rubro"] = _limitar_rubro(contenido.get("rubro"))

    contenido["anio"] = datetime.now().year
    contenido["promo"] = None
    contenido["testimonio"] = None
    contenido["destacado"] = None
    return contenido
