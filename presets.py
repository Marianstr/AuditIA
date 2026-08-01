"""
Catálogo de presets visuales para el generador de mockups.

Cada preset es un paquete cerrado de identidad visual: colores, tipografías
y redondeo de esquinas. La plantilla (mockup_base.html) no tiene ningún color
ni fuente escrito a mano: todo sale de aquí a través de variables CSS.

Para cambiar el aspecto de un mockup basta con pasarle otro preset. La
estructura del HTML no se toca.

Uso desde Flask:

    from presets import PRESETS, preset_por_id, google_fonts_url

    estilo = preset_por_id("calido_artesanal")
    render_template("mockup_base.html", estilo=estilo, ...)
"""

PRESETS = {

    "calido_artesanal": {
        "nombre": "Cálido artesanal",
        "descripcion": "Cercano, hecho a mano, de barrio.",
        "ejemplos": "Panaderías, cerámica, cafés, tiendas de barrio, floristerías.",
        "acento": "#c67139",
        "acento_suave": "#f0d9c3",
        "acento_oscuro": "#8f4b1e",
        "fondo": "#f5ead8",
        "superficie": "#fffaf1",
        "texto": "#201e1d",
        "texto_suave": "#6f665d",
        "fuente_titulo": '"Caprasimo", Georgia, serif',
        "fuente_cuerpo": '"Figtree", "Helvetica Neue", sans-serif',
        "fuentes_google": ["Caprasimo", "Figtree:wght@300;400;500;600;700"],
        "radio": "16px",
    },

    "clinico_limpio": {
        "nombre": "Clínico y limpio",
        "descripcion": "Confianza, rigor, higiene.",
        "ejemplos": "Clínicas, dentistas, fisioterapia, laboratorios, ópticas.",
        "acento": "#185fa5",
        "acento_suave": "#e3ecf5",
        "acento_oscuro": "#0f4478",
        "fondo": "#fbfcfd",
        "superficie": "#ffffff",
        "texto": "#042c53",
        "texto_suave": "#5d7186",
        "fuente_titulo": '"Manrope", "Helvetica Neue", sans-serif',
        "fuente_cuerpo": '"Manrope", "Helvetica Neue", sans-serif',
        "fuentes_google": ["Manrope:wght@400;500;600;700;800"],
        "radio": "6px",
    },

    "industrial_robusto": {
        "nombre": "Industrial robusto",
        "descripcion": "Sólido, sin florituras, de oficio.",
        "ejemplos": "Talleres, ferreterías, reformas, cerrajeros, transportes.",
        "acento": "#8c2f22",
        "acento_suave": "#dcd2c4",
        "acento_oscuro": "#5e1e15",
        "fondo": "#f3efe9",
        "superficie": "#fbf9f6",
        "texto": "#1c1815",
        "texto_suave": "#6a5f53",
        "fuente_titulo": '"Oswald", "Arial Narrow", sans-serif',
        "fuente_cuerpo": '"Lora", Georgia, serif',
        "fuentes_google": ["Oswald:wght@400;500;600;700", "Lora:wght@400;500;600"],
        "radio": "2px",
    },

    "elegante_premium": {
        "nombre": "Elegante premium",
        "descripcion": "Cuidado, editorial, de gama alta.",
        "ejemplos": "Joyerías, moda, interiorismo, hoteles, restaurantes de autor.",
        "acento": "#a65a4b",
        "acento_suave": "#e4dcd1",
        "acento_oscuro": "#71392e",
        "fondo": "#f6f2ec",
        "superficie": "#fffdfa",
        "texto": "#1c1917",
        "texto_suave": "#6b635c",
        "fuente_titulo": '"Bodoni Moda", "Times New Roman", serif',
        "fuente_cuerpo": '"Jost", "Helvetica Neue", sans-serif',
        "fuentes_google": ["Bodoni+Moda:opsz,wght@6..96,400;6..96,500;6..96,600", "Jost:wght@300;400;500;600"],
        "radio": "4px",
    },

    "fresco_joven": {
        "nombre": "Fresco y joven",
        "descripcion": "Natural, sano, de tú a tú.",
        "ejemplos": "Gimnasios, veganos, academias, coworkings, herbolarios.",
        "acento": "#3d7a4e",
        "acento_suave": "#dce8d2",
        "acento_oscuro": "#275132",
        "fondo": "#f4f5ee",
        "superficie": "#fdfefa",
        "texto": "#1f3324",
        "texto_suave": "#5e6b54",
        "fuente_titulo": '"Fraunces", Georgia, serif',
        "fuente_cuerpo": '"Karla", "Helvetica Neue", sans-serif',
        "fuentes_google": ["Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700", "Karla:wght@400;500;600;700"],
        "radio": "20px",
    },

    "corporativo_sobrio": {
        "nombre": "Corporativo sobrio",
        "descripcion": "Solvente, serio, profesional.",
        "ejemplos": "Gestorías, abogados, consultoras, seguros, inmobiliarias.",
        "acento": "#3f4a57",
        "acento_suave": "#dfe4e9",
        "acento_oscuro": "#252e38",
        "fondo": "#f7f8f9",
        "superficie": "#ffffff",
        "texto": "#141a21",
        "texto_suave": "#5a6673",
        "fuente_titulo": '"Archivo Black", "Helvetica Neue", sans-serif',
        "fuente_cuerpo": '"Space Grotesk", "Helvetica Neue", sans-serif',
        "fuentes_google": ["Archivo+Black", "Space+Grotesk:wght@400;500;600;700"],
        "radio": "8px",
    },

    "vivo_jugueton": {
        "nombre": "Vivo y juguetón",
        "descripcion": "Alegre, gráfico, con color sin miedo.",
        "ejemplos": "Heladerías, pastelerías, tiendas de niños, papelerías, ludotecas.",
        "acento": "#7c4dd0",
        "acento_suave": "#e9dcff",
        "acento_oscuro": "#54308f",
        "fondo": "#f7f2ff",
        "superficie": "#fffcf5",
        "texto": "#2c1a45",
        "texto_suave": "#6a5a80",
        "fuente_titulo": '"Bricolage Grotesque", "Helvetica Neue", sans-serif',
        "fuente_cuerpo": '"Nunito", "Helvetica Neue", sans-serif',
        "fuentes_google": ["Bricolage+Grotesque:opsz,wght@12..96,600;12..96,700;12..96,800", "Nunito:wght@400;500;600;700"],
        "radio": "22px",
    },

    "dulce_calido": {
        "nombre": "Dulce y cálido",
        "descripcion": "Afectivo, suave, de cuidarse.",
        "ejemplos": "Estudios de uñas, peluquerías, cafeterías, regalos, guarderías.",
        "acento": "#e8637f",
        "acento_suave": "#ffdfd7",
        "acento_oscuro": "#b23b56",
        "fondo": "#fff5f3",
        "superficie": "#fffcfb",
        "texto": "#40202a",
        "texto_suave": "#8a6470",
        "fuente_titulo": '"Baloo 2", "Helvetica Neue", sans-serif',
        "fuente_cuerpo": '"Quicksand", "Helvetica Neue", sans-serif',
        "fuentes_google": ["Baloo+2:wght@500;600;700;800", "Quicksand:wght@400;500;600;700"],
        "radio": "26px",
    },

}

PRESET_POR_DEFECTO = "calido_artesanal"


def preset_por_id(id_preset):
    """Devuelve el preset pedido. Si no existe, devuelve el de por defecto."""
    return PRESETS.get(id_preset, PRESETS[PRESET_POR_DEFECTO])


def google_fonts_url(id_preset):
    """
    Construye la URL de Google Fonts con las tipografías de ese preset.

    Es imprescindible: sin esto el navegador no tiene la fuente descargada
    y la página cae a la tipografía de reserva.
    """
    p = preset_por_id(id_preset)
    familias = "&".join("family=" + f for f in p["fuentes_google"])
    return "https://fonts.googleapis.com/css2?" + familias + "&display=swap"


def listar_presets():
    """
    Lista ligera para pintar el selector del panel de edición
    y para pasarle las opciones a la IA.
    """
    return [
        {
            "id": k,
            "nombre": v["nombre"],
            "descripcion": v["descripcion"],
            "ejemplos": v["ejemplos"],
            "acento": v["acento"],
        }
        for k, v in PRESETS.items()
    ]
