"""
Catálogo de parejas tipográficas para el generador de mockups.

Son independientes de los presets: un preset define color y radio, y trae una
pareja por defecto, pero el usuario puede cambiarla libremente por cualquiera
de este catálogo, o escribir familias de Google Fonts a mano (modo avanzado).

Todas las familias son de Google Fonts, gratuitas y de uso comercial libre.

Uso desde Flask:

    from tipografias import pareja_por_id, url_fuentes_pareja, listar_parejas

    par = pareja_por_id("bodoni_jost")
    render_template(..., fuentes_url=url_fuentes_pareja("bodoni_jost"))
"""

# Cada pareja define:
#   titulo / cuerpo    -> valor CSS completo, con familias de reserva
#   g_titulo / g_cuerpo-> especificación de Google Fonts, con pesos
#   grupo              -> para agrupar el desplegable del panel
#   nota               -> orientación breve para el usuario

PAREJAS = {

    # ---------------------------------------------------------------
    # SERIF EDITORIAL — prensa, cultura, marcas con historia
    # ---------------------------------------------------------------

    "playfair_source": {
        "nombre": "Playfair Display + Source Sans 3",
        "grupo": "Serif editorial",
        "nota": "Clásica y legible. Funciona casi en cualquier sector.",
        "titulo": '"Playfair Display", Georgia, serif',
        "cuerpo": '"Source Sans 3", "Helvetica Neue", sans-serif',
        "g_titulo": "Playfair+Display:wght@500;600;700;800",
        "g_cuerpo": "Source+Sans+3:wght@300;400;500;600",
    },
    "bodoni_jost": {
        "nombre": "Bodoni Moda + Jost",
        "grupo": "Serif editorial",
        "nota": "Contraste alto, aire de revista de moda.",
        "titulo": '"Bodoni Moda", "Times New Roman", serif',
        "cuerpo": '"Jost", "Helvetica Neue", sans-serif',
        "g_titulo": "Bodoni+Moda:opsz,wght@6..96,400;6..96,500;6..96,600",
        "g_cuerpo": "Jost:wght@300;400;500;600",
    },
    "lora_inter": {
        "nombre": "Lora + Inter",
        "grupo": "Serif editorial",
        "nota": "Cálida y muy legible en textos largos.",
        "titulo": '"Lora", Georgia, serif',
        "cuerpo": '"Inter", "Helvetica Neue", sans-serif',
        "g_titulo": "Lora:wght@500;600;700",
        "g_cuerpo": "Inter:wght@300;400;500;600",
    },
    "cormorant_montserrat": {
        "nombre": "Cormorant Garamond + Montserrat",
        "grupo": "Serif editorial",
        "nota": "Delicada y espaciosa. Ideal para gama alta.",
        "titulo": '"Cormorant Garamond", Garamond, serif',
        "cuerpo": '"Montserrat", "Helvetica Neue", sans-serif',
        "g_titulo": "Cormorant+Garamond:wght@500;600;700",
        "g_cuerpo": "Montserrat:wght@300;400;500;600",
    },
    "libre_baskerville_karla": {
        "nombre": "Libre Baskerville + Karla",
        "grupo": "Serif editorial",
        "nota": "Sobria y de confianza. Buena para servicios.",
        "titulo": '"Libre Baskerville", Georgia, serif',
        "cuerpo": '"Karla", "Helvetica Neue", sans-serif',
        "g_titulo": "Libre+Baskerville:wght@400;700",
        "g_cuerpo": "Karla:wght@400;500;600;700",
    },
    "crimson_worksans": {
        "nombre": "Crimson Pro + Work Sans",
        "grupo": "Serif editorial",
        "nota": "Literaria y tranquila. Libros, formación, cultura.",
        "titulo": '"Crimson Pro", Georgia, serif',
        "cuerpo": '"Work Sans", "Helvetica Neue", sans-serif',
        "g_titulo": "Crimson+Pro:wght@500;600;700",
        "g_cuerpo": "Work+Sans:wght@300;400;500;600",
    },
    "eb_garamond_lato": {
        "nombre": "EB Garamond + Lato",
        "grupo": "Serif editorial",
        "nota": "Atemporal y discreta. Nunca desentona.",
        "titulo": '"EB Garamond", Garamond, serif',
        "cuerpo": '"Lato", "Helvetica Neue", sans-serif',
        "g_titulo": "EB+Garamond:wght@500;600;700",
        "g_cuerpo": "Lato:wght@300;400;700",
    },
    "spectral_ibmplex": {
        "nombre": "Spectral + IBM Plex Sans",
        "grupo": "Serif editorial",
        "nota": "Técnica pero cálida. Consultoría, informes.",
        "titulo": '"Spectral", Georgia, serif',
        "cuerpo": '"IBM Plex Sans", "Helvetica Neue", sans-serif',
        "g_titulo": "Spectral:wght@500;600;700",
        "g_cuerpo": "IBM+Plex+Sans:wght@300;400;500;600",
    },

    # ---------------------------------------------------------------
    # SANS MODERNA — tecnología, servicios, marcas actuales
    # ---------------------------------------------------------------

    "manrope_manrope": {
        "nombre": "Manrope (títulos y cuerpo)",
        "grupo": "Sans moderna",
        "nota": "Limpia y neutra. Segura para clínicas y servicios.",
        "titulo": '"Manrope", "Helvetica Neue", sans-serif',
        "cuerpo": '"Manrope", "Helvetica Neue", sans-serif',
        "g_titulo": "Manrope:wght@400;500;600;700;800",
        "g_cuerpo": "",
    },
    "space_inter": {
        "nombre": "Space Grotesk + Inter",
        "grupo": "Sans moderna",
        "nota": "Con personalidad sin gritar. Tecnología, estudios.",
        "titulo": '"Space Grotesk", "Helvetica Neue", sans-serif',
        "cuerpo": '"Inter", "Helvetica Neue", sans-serif',
        "g_titulo": "Space+Grotesk:wght@500;600;700",
        "g_cuerpo": "Inter:wght@300;400;500;600",
    },
    "outfit_outfit": {
        "nombre": "Outfit (títulos y cuerpo)",
        "grupo": "Sans moderna",
        "nota": "Geométrica y amable. Muy versátil.",
        "titulo": '"Outfit", "Helvetica Neue", sans-serif',
        "cuerpo": '"Outfit", "Helvetica Neue", sans-serif',
        "g_titulo": "Outfit:wght@300;400;500;600;700",
        "g_cuerpo": "",
    },
    "poppins_inter": {
        "nombre": "Poppins + Inter",
        "grupo": "Sans moderna",
        "nota": "Redonda y cercana. Comercio y consumo.",
        "titulo": '"Poppins", "Helvetica Neue", sans-serif',
        "cuerpo": '"Inter", "Helvetica Neue", sans-serif',
        "g_titulo": "Poppins:wght@500;600;700",
        "g_cuerpo": "Inter:wght@300;400;500;600",
    },
    "dmsans_dmsans": {
        "nombre": "DM Sans (títulos y cuerpo)",
        "grupo": "Sans moderna",
        "nota": "Discreta y muy legible. Cuando el texto manda.",
        "titulo": '"DM Sans", "Helvetica Neue", sans-serif',
        "cuerpo": '"DM Sans", "Helvetica Neue", sans-serif',
        "g_titulo": "DM+Sans:wght@400;500;600;700",
        "g_cuerpo": "",
    },
    "plusjakarta_inter": {
        "nombre": "Plus Jakarta Sans + Inter",
        "grupo": "Sans moderna",
        "nota": "Actual y profesional. Software, agencias.",
        "titulo": '"Plus Jakarta Sans", "Helvetica Neue", sans-serif',
        "cuerpo": '"Inter", "Helvetica Neue", sans-serif',
        "g_titulo": "Plus+Jakarta+Sans:wght@500;600;700;800",
        "g_cuerpo": "Inter:wght@300;400;500;600",
    },
    "figtree_figtree": {
        "nombre": "Figtree (títulos y cuerpo)",
        "grupo": "Sans moderna",
        "nota": "Amable y clara. Buena para todo público.",
        "titulo": '"Figtree", "Helvetica Neue", sans-serif',
        "cuerpo": '"Figtree", "Helvetica Neue", sans-serif',
        "g_titulo": "Figtree:wght@300;400;500;600;700;800",
        "g_cuerpo": "",
    },
    "sora_karla": {
        "nombre": "Sora + Karla",
        "grupo": "Sans moderna",
        "nota": "Angular y despierta. Startups, innovación.",
        "titulo": '"Sora", "Helvetica Neue", sans-serif',
        "cuerpo": '"Karla", "Helvetica Neue", sans-serif',
        "g_titulo": "Sora:wght@500;600;700",
        "g_cuerpo": "Karla:wght@400;500;600",
    },
    "urbanist_urbanist": {
        "nombre": "Urbanist (títulos y cuerpo)",
        "grupo": "Sans moderna",
        "nota": "Fina y elegante sin ser serif.",
        "titulo": '"Urbanist", "Helvetica Neue", sans-serif',
        "cuerpo": '"Urbanist", "Helvetica Neue", sans-serif',
        "g_titulo": "Urbanist:wght@300;400;500;600;700",
        "g_cuerpo": "",
    },
    "publicsans_publicsans": {
        "nombre": "Public Sans (títulos y cuerpo)",
        "grupo": "Sans moderna",
        "nota": "Institucional y sólida. Gestorías, seguros.",
        "titulo": '"Public Sans", "Helvetica Neue", sans-serif',
        "cuerpo": '"Public Sans", "Helvetica Neue", sans-serif',
        "g_titulo": "Public+Sans:wght@400;500;600;700;800",
        "g_cuerpo": "",
    },

    # ---------------------------------------------------------------
    # DISPLAY CON CARÁCTER — cuando la marca tiene que destacar
    # ---------------------------------------------------------------

    "caprasimo_figtree": {
        "nombre": "Caprasimo + Figtree",
        "grupo": "Display con carácter",
        "nota": "Rotunda y simpática. Comercio de barrio, hostelería.",
        "titulo": '"Caprasimo", Georgia, serif',
        "cuerpo": '"Figtree", "Helvetica Neue", sans-serif',
        "g_titulo": "Caprasimo",
        "g_cuerpo": "Figtree:wght@300;400;500;600;700",
    },
    "fraunces_karla": {
        "nombre": "Fraunces + Karla",
        "grupo": "Display con carácter",
        "nota": "Artesana y con alma. Producto natural, cuidado.",
        "titulo": '"Fraunces", Georgia, serif',
        "cuerpo": '"Karla", "Helvetica Neue", sans-serif',
        "g_titulo": "Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700",
        "g_cuerpo": "Karla:wght@400;500;600;700",
    },
    "bricolage_nunito": {
        "nombre": "Bricolage Grotesque + Nunito",
        "grupo": "Display con carácter",
        "nota": "Gráfica y actual. Marcas jóvenes y alegres.",
        "titulo": '"Bricolage Grotesque", "Helvetica Neue", sans-serif',
        "cuerpo": '"Nunito", "Helvetica Neue", sans-serif',
        "g_titulo": "Bricolage+Grotesque:opsz,wght@12..96,600;12..96,700;12..96,800",
        "g_cuerpo": "Nunito:wght@400;500;600;700",
    },
    "archivoblack_space": {
        "nombre": "Archivo Black + Space Grotesk",
        "grupo": "Display con carácter",
        "nota": "Contundente. Cuando hay que sonar firme.",
        "titulo": '"Archivo Black", "Helvetica Neue", sans-serif',
        "cuerpo": '"Space Grotesk", "Helvetica Neue", sans-serif',
        "g_titulo": "Archivo+Black",
        "g_cuerpo": "Space+Grotesk:wght@400;500;600;700",
    },
    "oswald_lora": {
        "nombre": "Oswald + Lora",
        "grupo": "Display con carácter",
        "nota": "Condensada y de oficio. Talleres, obra, transporte.",
        "titulo": '"Oswald", "Arial Narrow", sans-serif',
        "cuerpo": '"Lora", Georgia, serif',
        "g_titulo": "Oswald:wght@400;500;600;700",
        "g_cuerpo": "Lora:wght@400;500;600",
    },
    "abrilfatface_lato": {
        "nombre": "Abril Fatface + Lato",
        "grupo": "Display con carácter",
        "nota": "Titular de cartel. Mucho impacto en poco espacio.",
        "titulo": '"Abril Fatface", Georgia, serif',
        "cuerpo": '"Lato", "Helvetica Neue", sans-serif',
        "g_titulo": "Abril+Fatface",
        "g_cuerpo": "Lato:wght@300;400;700",
    },
    "marcellus_karla": {
        "nombre": "Marcellus + Karla",
        "grupo": "Display con carácter",
        "nota": "Clásica romana. Restauración, joyería, notarías.",
        "titulo": '"Marcellus", Georgia, serif',
        "cuerpo": '"Karla", "Helvetica Neue", sans-serif',
        "g_titulo": "Marcellus",
        "g_cuerpo": "Karla:wght@400;500;600;700",
    },
    "unbounded_inter": {
        "nombre": "Unbounded + Inter",
        "grupo": "Display con carácter",
        "nota": "Futurista y llamativa. Tecnología, eventos.",
        "titulo": '"Unbounded", "Helvetica Neue", sans-serif',
        "cuerpo": '"Inter", "Helvetica Neue", sans-serif',
        "g_titulo": "Unbounded:wght@500;600;700",
        "g_cuerpo": "Inter:wght@300;400;500;600",
    },
    "syne_inter": {
        "nombre": "Syne + Inter",
        "grupo": "Display con carácter",
        "nota": "De galería de arte. Estudios creativos, cultura.",
        "titulo": '"Syne", "Helvetica Neue", sans-serif',
        "cuerpo": '"Inter", "Helvetica Neue", sans-serif',
        "g_titulo": "Syne:wght@600;700;800",
        "g_cuerpo": "Inter:wght@300;400;500;600",
    },
    "instrument_dmsans": {
        "nombre": "Instrument Serif + DM Sans",
        "grupo": "Display con carácter",
        "nota": "Fina y sofisticada. Marcas de nicho.",
        "titulo": '"Instrument Serif", Georgia, serif',
        "cuerpo": '"DM Sans", "Helvetica Neue", sans-serif',
        "g_titulo": "Instrument+Serif:ital@0;1",
        "g_cuerpo": "DM+Sans:wght@400;500;600;700",
    },

    # ---------------------------------------------------------------
    # AMABLE Y REDONDA — infancia, cuidado, ocio, bienestar
    # ---------------------------------------------------------------

    "baloo_quicksand": {
        "nombre": "Baloo 2 + Quicksand",
        "grupo": "Amable y redonda",
        "nota": "Dulce y acogedora. Estética, infancia, cafés.",
        "titulo": '"Baloo 2", "Helvetica Neue", sans-serif',
        "cuerpo": '"Quicksand", "Helvetica Neue", sans-serif',
        "g_titulo": "Baloo+2:wght@500;600;700;800",
        "g_cuerpo": "Quicksand:wght@400;500;600;700",
    },
    "nunito_nunito": {
        "nombre": "Nunito (títulos y cuerpo)",
        "grupo": "Amable y redonda",
        "nota": "Cercana y sin aristas. Servicios de trato directo.",
        "titulo": '"Nunito", "Helvetica Neue", sans-serif',
        "cuerpo": '"Nunito", "Helvetica Neue", sans-serif',
        "g_titulo": "Nunito:wght@400;500;600;700;800",
        "g_cuerpo": "",
    },
    "comfortaa_nunitosans": {
        "nombre": "Comfortaa + Nunito Sans",
        "grupo": "Amable y redonda",
        "nota": "Muy suave. Bienestar, spa, guarderías.",
        "titulo": '"Comfortaa", "Helvetica Neue", sans-serif',
        "cuerpo": '"Nunito Sans", "Helvetica Neue", sans-serif',
        "g_titulo": "Comfortaa:wght@500;600;700",
        "g_cuerpo": "Nunito+Sans:wght@300;400;600;700",
    },
    "quicksand_quicksand": {
        "nombre": "Quicksand (títulos y cuerpo)",
        "grupo": "Amable y redonda",
        "nota": "Ligera y limpia. Productos naturales.",
        "titulo": '"Quicksand", "Helvetica Neue", sans-serif',
        "cuerpo": '"Quicksand", "Helvetica Neue", sans-serif',
        "g_titulo": "Quicksand:wght@400;500;600;700",
        "g_cuerpo": "",
    },
    "shantell_nunito": {
        "nombre": "Shantell Sans + Nunito",
        "grupo": "Amable y redonda",
        "nota": "Manuscrita informal. Papelerías, talleres creativos.",
        "titulo": '"Shantell Sans", "Comic Sans MS", cursive',
        "cuerpo": '"Nunito", "Helvetica Neue", sans-serif',
        "g_titulo": "Shantell+Sans:wght@500;600;700",
        "g_cuerpo": "Nunito:wght@400;500;600;700",
    },
    "fredoka_nunito": {
        "nombre": "Fredoka + Nunito",
        "grupo": "Amable y redonda",
        "nota": "Juguetona y directa. Heladerías, ludotecas.",
        "titulo": '"Fredoka", "Helvetica Neue", sans-serif',
        "cuerpo": '"Nunito", "Helvetica Neue", sans-serif',
        "g_titulo": "Fredoka:wght@500;600;700",
        "g_cuerpo": "Nunito:wght@400;500;600;700",
    },

    # ---------------------------------------------------------------
    # TÉCNICA Y PRECISA — ingeniería, datos, oficios especializados
    # ---------------------------------------------------------------

    "ibmplex_ibmplex": {
        "nombre": "IBM Plex Sans (títulos y cuerpo)",
        "grupo": "Técnica y precisa",
        "nota": "Ingenieril y clara. Industria, software.",
        "titulo": '"IBM Plex Sans", "Helvetica Neue", sans-serif',
        "cuerpo": '"IBM Plex Sans", "Helvetica Neue", sans-serif',
        "g_titulo": "IBM+Plex+Sans:wght@400;500;600;700",
        "g_cuerpo": "",
    },
    "chakra_inter": {
        "nombre": "Chakra Petch + Inter",
        "grupo": "Técnica y precisa",
        "nota": "Angular y técnica. Automoción, gaming, seguridad.",
        "titulo": '"Chakra Petch", "Helvetica Neue", sans-serif',
        "cuerpo": '"Inter", "Helvetica Neue", sans-serif',
        "g_titulo": "Chakra+Petch:wght@500;600;700",
        "g_cuerpo": "Inter:wght@300;400;500;600",
    },
    "rajdhani_inter": {
        "nombre": "Rajdhani + Inter",
        "grupo": "Técnica y precisa",
        "nota": "Condensada y deportiva. Gimnasios, competición.",
        "titulo": '"Rajdhani", "Arial Narrow", sans-serif',
        "cuerpo": '"Inter", "Helvetica Neue", sans-serif',
        "g_titulo": "Rajdhani:wght@500;600;700",
        "g_cuerpo": "Inter:wght@300;400;500;600",
    },
    "barlowcondensed_barlow": {
        "nombre": "Barlow Condensed + Barlow",
        "grupo": "Técnica y precisa",
        "nota": "Estrecha y eficiente. Logística, obra, señalética.",
        "titulo": '"Barlow Condensed", "Arial Narrow", sans-serif',
        "cuerpo": '"Barlow", "Helvetica Neue", sans-serif',
        "g_titulo": "Barlow+Condensed:wght@500;600;700",
        "g_cuerpo": "Barlow:wght@300;400;500;600",
    },
    "archivo_archivo": {
        "nombre": "Archivo (títulos y cuerpo)",
        "grupo": "Técnica y precisa",
        "nota": "Robusta y funcional. Industria, mayoristas.",
        "titulo": '"Archivo", "Helvetica Neue", sans-serif',
        "cuerpo": '"Archivo", "Helvetica Neue", sans-serif',
        "g_titulo": "Archivo:wght@400;500;600;700;800",
        "g_cuerpo": "",
    },
    "jetbrains_inter": {
        "nombre": "JetBrains Mono + Inter",
        "grupo": "Técnica y precisa",
        "nota": "Monoespaciada. Informática, ciberseguridad.",
        "titulo": '"JetBrains Mono", "Courier New", monospace',
        "cuerpo": '"Inter", "Helvetica Neue", sans-serif',
        "g_titulo": "JetBrains+Mono:wght@500;600;700",
        "g_cuerpo": "Inter:wght@300;400;500;600",
    },
}

PAREJA_POR_DEFECTO = "caprasimo_figtree"

GRUPOS = [
    "Serif editorial",
    "Sans moderna",
    "Display con carácter",
    "Amable y redonda",
    "Técnica y precisa",
]


def pareja_por_id(id_pareja):
    """Devuelve la pareja pedida, o la de por defecto si no existe."""
    return PAREJAS.get(id_pareja, PAREJAS[PAREJA_POR_DEFECTO])


def url_fuentes_pareja(id_pareja):
    """URL de Google Fonts con las familias y pesos de esa pareja."""
    p = pareja_por_id(id_pareja)
    familias = [p["g_titulo"]]
    if p["g_cuerpo"]:
        familias.append(p["g_cuerpo"])
    return ("https://fonts.googleapis.com/css2?"
            + "&".join("family=" + f for f in familias)
            + "&display=swap")


def url_fuentes_libres(familia_titulo, familia_cuerpo=None):
    """
    Modo avanzado: construye la URL a partir de nombres escritos por el
    usuario (por ejemplo "Josefin Sans"). Se cargan varios pesos por si
    la familia los tiene; Google ignora los que no existan.

    Ojo: si el nombre está mal escrito, Google devuelve un CSS vacío y la
    página cae a la tipografía de reserva sin avisar. Conviene validar
    antes de guardar.
    """
    def spec(nombre):
        return nombre.strip().replace(" ", "+") + ":wght@300;400;500;600;700"

    familias = [spec(familia_titulo)]
    if familia_cuerpo and familia_cuerpo.strip():
        familias.append(spec(familia_cuerpo))
    return ("https://fonts.googleapis.com/css2?"
            + "&".join("family=" + f for f in familias)
            + "&display=swap")


def css_familia(nombre, con_serifa=False):
    """
    Convierte un nombre suelto en un valor CSS con reserva.
    Se usa en modo avanzado para --fuente-titulo y --fuente-cuerpo.
    """
    reserva = "Georgia, serif" if con_serifa else '"Helvetica Neue", sans-serif'
    return '"%s", %s' % (nombre.strip(), reserva)


def listar_parejas():
    """Lista ligera y ordenada por grupo, para pintar el desplegable."""
    salida = []
    for grupo in GRUPOS:
        for k, v in PAREJAS.items():
            if v["grupo"] == grupo:
                salida.append({
                    "id": k,
                    "nombre": v["nombre"],
                    "grupo": grupo,
                    "nota": v["nota"],
                })
    return salida
