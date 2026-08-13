import io
import json
import os
import re
import secrets
from datetime import datetime
from functools import wraps

import openpyxl
import requests
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, send_file, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash

from scraper import buscar_negocios_google
from scoring.lead_scorer import calcular_score, clasificar_lead, recomendar_servicios
from scoring.analizador_web import analizar_web
from generador_propuesta import generar_propuesta
from generador_landing import generar_contenido_landing
from presets import preset_por_id, google_fonts_url, listar_presets
from tipografias import pareja_por_id, url_fuentes_pareja, url_fuentes_libres, css_familia, listar_parejas, GRUPOS
from buscador_fotos import buscar_foto_categoria, buscar_fotos_categoria

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or "auditia-secret-key-cambiar-en-produccion"

AUTH_FILE = "auth.json"
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
BREVO_API_KEY = os.environ.get("BREVO_API_KEY")
BREVO_SENDER_EMAIL = os.environ.get("BREVO_SENDER_EMAIL", "no-reply@auditia.digital")
BREVO_SENDER_NOMBRE = os.environ.get("BREVO_SENDER_NOMBRE", "AuditIA")
from db import cargar_historial_db, guardar_historial_db, crear_tabla_historial
crear_tabla_historial()
from db import cargar_clientes_db, guardar_clientes_db, crear_tabla_clientes
crear_tabla_clientes()
from db import cargar_facturado_db, guardar_facturado_db, crear_tabla_facturado
crear_tabla_facturado()
from db import cargar_proyectos_db, guardar_proyectos_db, crear_tabla_proyectos
crear_tabla_proyectos()


def cargar_auth():
    from db import cargar_auth_db, crear_tabla_usuarios, guardar_auth_db
    crear_tabla_usuarios()
    datos = cargar_auth_db()
    if not datos:
        datos = {
            "admin": {
                "password": generate_password_hash("auditia2026", method="pbkdf2:sha256"),
                "limite": None, "usadas": 0, "plan": "agency", "verificado": True,
            },
            "ariel": {
                "password": generate_password_hash("utn2026", method="pbkdf2:sha256"),
                "limite": 10, "usadas": 0, "plan": "pro", "verificado": True,
            },
            "profe2": {
                "password": generate_password_hash("utn2026", method="pbkdf2:sha256"),
                "limite": 10, "usadas": 0, "plan": "pro", "verificado": True,
            },
            "visitante": {
                "password": generate_password_hash("123", method="pbkdf2:sha256"),
                "limite": 15, "usadas": 0, "plan": "free", "verificado": True,
            },
        }
        guardar_auth_db(datos)
    return datos

def guardar_auth(datos):
    from db import guardar_auth_db
    guardar_auth_db(datos)


cargar_auth()


# ---- Planes y control de acceso por plan ----
PLANES = {
    "free":   {"limite": 5,   "funciones": {"scoring", "export_excel"}},
    "pro":    {"limite": 50,  "funciones": {"scoring", "export_excel", "crm", "proyectos", "export_pdf", "propuesta_visual"}},
    "agency": {"limite": 200, "funciones": {"scoring", "export_excel", "crm", "proyectos", "export_pdf", "multiusuario", "busquedas_extra", "propuesta_visual"}},
}

def plan_de(registro_usuario):
    """Devuelve el plan del usuario. Usa el campo 'plan' si existe;
    si no, lo deduce del 'limite' ya guardado."""
    if not registro_usuario:
        return "free"
    if registro_usuario.get("plan") in PLANES:
        return registro_usuario["plan"]
    limite = registro_usuario.get("limite")
    if limite is None:
        return "agency"
    if limite >= 200:
        return "agency"
    if limite >= 50:
        return "pro"
    return "free"

def plan_permite(registro_usuario, funcion):
    """True si el plan del usuario incluye esa función."""
    plan = plan_de(registro_usuario)
    return funcion in PLANES[plan]["funciones"]


def enviar_email_verificacion(email, token):
    """Envía el email de verificación de cuenta usando la API transaccional de Brevo."""
    if not BREVO_API_KEY:
        return
    link = f"https://www.auditia.digital/verificar/{token}"
    try:
        response = requests.post(
            "https://api.brevo.com/v3/smtp/email",
            headers={
                "api-key": BREVO_API_KEY,
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            json={
                "sender": {"name": BREVO_SENDER_NOMBRE, "email": BREVO_SENDER_EMAIL},
                "to": [{"email": email}],
                "subject": "Verificá tu cuenta de AuditIA",
                "htmlContent": (
                    "<p>Hola,</p>"
                    "<p>Gracias por registrarte en AuditIA. Para activar tu cuenta, hacé clic en el siguiente enlace:</p>"
                    f'<p><a href="{link}">Verificar mi cuenta</a></p>'
                    "<p>Si el enlace no funciona, copiá y pegá esta dirección en tu navegador:</p>"
                    f"<p>{link}</p>"
                    "<p>Si no creaste esta cuenta, podés ignorar este email.</p>"
                ),
            },
            timeout=10,
        )
        print(f"[Brevo] POST /smtp/email para {email} -> status_code={response.status_code}, response={response.text}")
    except requests.RequestException as e:
        print(f"[Brevo] Error de conexión al enviar email de verificación a {email}: {e}")


def login_required(f):
    @wraps(f)
    def decorada(*args, **kwargs):
        if not session.get("usuario"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorada


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        auth = cargar_auth()
        usuario = request.form.get("usuario", "")
        password = request.form.get("password", "")
        registro = auth.get(usuario)
        if registro and check_password_hash(registro.get("password", ""), password):
            if not registro.get("verificado", False):
                error = "Todavía no verificaste tu email. Revisá tu bandeja de entrada (y spam) y hacé clic en el enlace de verificación antes de iniciar sesión."
            else:
                session["usuario"] = usuario
                return redirect(url_for("index"))
        else:
            error = "Usuario o contraseña incorrectos"
    return render_template("login.html", error=error)


@app.route("/registro", methods=["GET", "POST"])
def registro():
    error = None
    mensaje = None
    if request.method == "POST":
        auth = cargar_auth()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        if email in auth:
            error = "Ese email ya está registrado."
        elif not EMAIL_RE.match(email):
            error = "Ingresá un email válido."
        elif len(password) < 6:
            error = "La contraseña debe tener al menos 6 caracteres."
        else:
            token = secrets.token_urlsafe(32)
            auth[email] = {
                "password": generate_password_hash(password, method="pbkdf2:sha256"),
                "limite": 5,
                "usadas": 0,
                "verificado": False,
                "token_verificacion": token,
            }
            guardar_auth(auth)
            enviar_email_verificacion(email, token)
            mensaje = f"¡Listo! Te enviamos un email a {email} para verificar tu cuenta. Revisá tu bandeja de entrada (y spam) y hacé clic en el enlace antes de iniciar sesión."
    return render_template("registro.html", error=error, mensaje=mensaje)


@app.route("/verificar/<token>")
def verificar(token):
    auth = cargar_auth()
    for usuario, registro_usuario in auth.items():
        if registro_usuario.get("token_verificacion") == token:
            registro_usuario["verificado"] = True
            registro_usuario["token_verificacion"] = None
            guardar_auth(auth)
            return render_template("verificado.html", exito=True)
    return render_template("verificado.html", exito=False)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))


@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/app")
@login_required
def index():
    plan_usuario = plan_de(cargar_auth().get(session["usuario"]))
    return render_template("index.html", usuario=session["usuario"], plan=plan_usuario)


@app.route("/buscar", methods=["POST"])
@login_required
def buscar():
    modo = request.json.get("modo", "categoria")
    tipo = request.json.get("tipo")
    ciudad = request.json.get("ciudad")
    zona = request.json.get("zona")
    nombre_negocio = request.json.get("nombre_negocio")

    auth = cargar_auth()
    registro_usuario = auth.get(session["usuario"])
    limite = registro_usuario.get("limite")
    usadas = registro_usuario.get("usadas", 0)
    if limite is not None and usadas >= limite:
        return jsonify({"error": "Has alcanzado el límite de búsquedas de tu plan."}), 403

    try:
        if modo == "nombre":
            negocios = buscar_negocios_google(consulta_directa=nombre_negocio)
        else:
            negocios = buscar_negocios_google(tipo, ciudad, zona)
    except Exception:
        return jsonify({"error": "Ocurrió un error al buscar en Google Maps. Intentá de nuevo más tarde."}), 502

    registro_usuario["usadas"] = usadas + 1
    guardar_auth(auth)

    resultados = []
    for negocio in negocios:
        score = calcular_score(negocio)
        clasificacion = clasificar_lead(score)
        servicios = recomendar_servicios(negocio)
        resultados.append({
            "nombre": negocio["nombre"],
            "direccion": negocio["direccion"],
            "telefono": negocio["telefono"],
            "web": negocio["web"],
            "rating": negocio["rating"],
            "cantidad_resenas": negocio["cantidad_resenas"],
            "score": score,
            "clasificacion": clasificacion,
            "servicios": servicios,
            "primary_type": negocio.get("primary_type", ""),
            "categoria_google": negocio.get("categoria_google", ""),
            "tipos": negocio.get("tipos", []),
        })
    resultados.sort(key=lambda x: x["score"], reverse=True)
    registro = {
        "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "tipo": nombre_negocio if modo == "nombre" else tipo,
        "ciudad": "" if modo == "nombre" else ciudad,
        "zona": "" if modo == "nombre" else (zona or ""),
        "modo": modo,
        "total": len(resultados),
        "calientes": len([r for r in resultados if r["clasificacion"] == "caliente"]),
        "tibios": len([r for r in resultados if r["clasificacion"] == "tibio"]),
        "frios": len([r for r in resultados if r["clasificacion"] == "frio"]),
        "resultados": resultados,
        "usuario": session["usuario"]
    }
    try:
        historial = cargar_historial_db()
    except FileNotFoundError:
        historial = []
    historial.append(registro)
    indice = len(historial) - 1
    guardar_historial_db(historial)
    return jsonify({"resultados": resultados, "indice": indice})


@app.route("/analizar-web", methods=["POST"])
@login_required
def analizar_web_ruta():
    url = request.json.get("web", "")
    if not url or url == "No tiene":
        return jsonify({"error": "Este lead no tiene sitio web para analizar."}), 400
    resultado = analizar_web(url)
    if not resultado.get("ok"):
        return jsonify({"error": resultado.get("error", "No se pudo analizar la web.")}), 502
    return jsonify(resultado)


@app.route("/generar-propuesta", methods=["POST"])
@login_required
def generar_propuesta_ruta():
    datos = request.json
    formato = datos.get("formato", "whatsapp")
    datos_lead = datos.get("lead", {})
    resultado = generar_propuesta(datos_lead, formato)
    if not resultado.get("ok"):
        return jsonify({"error": resultado.get("error", "No se pudo generar la propuesta.")}), 502
    return jsonify({"texto": resultado["texto"]})


@app.route("/mockup")
@login_required
def mockup_propuesta():
    registro_usuario = cargar_auth().get(session["usuario"])
    if not plan_permite(registro_usuario, "propuesta_visual"):
        return "Esta función está disponible en los planes Pro y Agency.", 403
    nombre = request.args.get("nombre", "Tu Negocio")
    categoria = request.args.get("categoria", "Tu rubro")
    eslogan = request.args.get("eslogan", "Así podría verse tu negocio en internet.")
    eslogan_corto = request.args.get("eslogan_corto", "Bienvenidos.")
    foto_url = buscar_foto_categoria(categoria) or "https://images.unsplash.com/photo-1528825871115-3581a5387919?w=1000&q=80"
    return render_template("mockup.html",
                           nombre=nombre,
                           categoria=categoria,
                           eslogan=eslogan,
                           eslogan_corto=eslogan_corto,
                           foto_url=foto_url)


@app.route("/mockup-landing")
@login_required
def mockup_landing():
    registro_usuario = cargar_auth().get(session["usuario"])
    if not plan_permite(registro_usuario, "propuesta_visual"):
        return "Esta función está disponible en los planes Pro y Agency.", 403

    def _lista(nombre_campo):
        valores = request.args.getlist(nombre_campo)
        if valores:
            return valores
        crudo = request.args.get(nombre_campo)
        return [v.strip() for v in crudo.split(",") if v.strip()] if crudo else []

    def _numero(nombre_campo, tipo):
        crudo = request.args.get(nombre_campo)
        if crudo in (None, ""):
            return None
        try:
            return tipo(crudo)
        except (TypeError, ValueError):
            return None

    lead = {
        "nombre": request.args.get("nombre", "Tu Negocio"),
        "direccion": request.args.get("direccion", ""),
        "telefono": request.args.get("telefono", ""),
        "web": request.args.get("web", ""),
        "rating": _numero("rating", float),
        "cantidad_resenas": _numero("cantidad_resenas", int),
        "score": _numero("score", float),
        "clasificacion": request.args.get("clasificacion", ""),
        "servicios": _lista("servicios"),
        "primary_type": request.args.get("primary_type", ""),
        "categoria_google": request.args.get("categoria_google", ""),
        "tipos": _lista("tipos"),
    }

    c = generar_contenido_landing(lead)

    preset_solicitado = request.args.get("preset")
    ids_validos = {p["id"] for p in listar_presets()}
    id_preset = preset_solicitado if preset_solicitado in ids_validos else c.get("preset")

    estilo = dict(preset_por_id(id_preset))
    fuentes_url = google_fonts_url(id_preset)

    tipografia_solicitada = request.args.get("tipografia")
    ids_tipografia_validas = {p["id"] for p in listar_parejas()}
    if tipografia_solicitada in ids_tipografia_validas:
        pareja = pareja_por_id(tipografia_solicitada)
        estilo["fuente_titulo"] = pareja["titulo"]
        estilo["fuente_cuerpo"] = pareja["cuerpo"]
        fuentes_url = url_fuentes_pareja(tipografia_solicitada)

    fuente_titulo_libre = (request.args.get("fuente_titulo") or "").strip()
    fuente_cuerpo_libre = (request.args.get("fuente_cuerpo") or "").strip()
    if fuente_titulo_libre:
        estilo["fuente_titulo"] = css_familia(fuente_titulo_libre)
        if fuente_cuerpo_libre:
            estilo["fuente_cuerpo"] = css_familia(fuente_cuerpo_libre)
        fuentes_url = url_fuentes_libres(fuente_titulo_libre, fuente_cuerpo_libre or None)

    def _hex_valido(valor):
        return bool(re.match(r"^#[0-9a-fA-F]{6}$", valor or ""))

    def _radio_valido(valor):
        try:
            numero = float(valor)
        except (TypeError, ValueError):
            return None
        return numero if 0 <= numero <= 30 else None

    def _escala_valida(valor):
        try:
            numero = float(valor)
        except (TypeError, ValueError):
            return None
        return numero if 0.8 <= numero <= 1.2 else None

    def _foto_pos_valida(valor):
        try:
            numero = float(valor)
        except (TypeError, ValueError):
            return None
        return numero if 0 <= numero <= 100 else None

    def _foto_zoom_valido(valor):
        try:
            numero = float(valor)
        except (TypeError, ValueError):
            return None
        return numero if 50 <= numero <= 200 else None

    campos_color = {
        "color_acento": "acento",
        "color_fondo": "fondo",
        "color_superficie": "superficie",
        "color_texto": "texto",
        "color_texto_suave": "texto_suave",
    }
    for parametro, clave_estilo in campos_color.items():
        valor = request.args.get(parametro)
        if _hex_valido(valor):
            estilo[clave_estilo] = valor

    radio_valido = _radio_valido(request.args.get("radio"))
    if radio_valido is not None:
        estilo["radio"] = f"{radio_valido:g}px"

    estilo["escala_titulo"] = "1"
    escala_titulo_valida = _escala_valida(request.args.get("escala_titulo"))
    if escala_titulo_valida is not None:
        estilo["escala_titulo"] = f"{escala_titulo_valida:g}"

    estilo["escala_cuerpo"] = "1"
    escala_cuerpo_valida = _escala_valida(request.args.get("escala_cuerpo"))
    if escala_cuerpo_valida is not None:
        estilo["escala_cuerpo"] = f"{escala_cuerpo_valida:g}"

    estilo["foto_pos_x"] = "50"
    foto_pos_x_valida = _foto_pos_valida(request.args.get("foto_pos_x"))
    if foto_pos_x_valida is not None:
        estilo["foto_pos_x"] = f"{foto_pos_x_valida:g}"

    estilo["foto_pos_y"] = "50"
    foto_pos_y_valida = _foto_pos_valida(request.args.get("foto_pos_y"))
    if foto_pos_y_valida is not None:
        estilo["foto_pos_y"] = f"{foto_pos_y_valida:g}"

    estilo["foto_zoom"] = "100"
    foto_zoom_valido = _foto_zoom_valido(request.args.get("foto_zoom"))
    if foto_zoom_valido is not None:
        estilo["foto_zoom"] = f"{foto_zoom_valido:g}"

    estructura = request.args.get("estructura", "partido")
    if estructura not in ("partido", "foto", "tipografica"):
        estructura = "partido"

    tratamiento_foto = request.args.get("tratamiento_foto", "sin")
    if tratamiento_foto not in ("sin", "duotono", "bn"):
        tratamiento_foto = "sin"

    fondo_foto = request.args.get("fondo_foto", "ampliada")
    if fondo_foto not in ("ampliada", "liso", "acento"):
        fondo_foto = "ampliada"

    negocio = {
        "nombre": lead["nombre"],
        "direccion": lead["direccion"],
        "telefono": lead["telefono"],
        "rubro": c.get("rubro", ""),
        "horario": "",
        "email": "",
    }

    termino_foto_ia = (c.get("termino_foto") or "").strip()
    if termino_foto_ia:
        fotos = buscar_fotos_categoria(termino_foto_ia, cantidad=4, ya_en_ingles=True)
    else:
        categoria_fotos = (lead.get("categoria_google") or "").strip() or (lead.get("primary_type") or "").strip()
        fotos = buscar_fotos_categoria(categoria_fotos, cantidad=4)

    return render_template("mockup_base.html",
                           negocio=negocio,
                           c=c,
                           estilo=estilo,
                           fuentes_url=fuentes_url,
                           presets=listar_presets(),
                           parejas=listar_parejas(),
                           grupos=GRUPOS,
                           preset_por_id=preset_por_id,
                           pareja_por_id=pareja_por_id,
                           preset_actual=id_preset,
                           estructura=estructura,
                           fotos=fotos,
                           tratamiento_foto=tratamiento_foto,
                           fondo_foto=fondo_foto)


@app.route("/historial/resultados/<int:indice>")
@login_required
def resultados_historial(indice):
    try:
        historial = cargar_historial_db()
        registro = historial[indice]
    except (FileNotFoundError, IndexError):
        return jsonify({"error": "Auditoría no encontrada"}), 404
    if registro.get("usuario", "admin") != session["usuario"]:
        return jsonify({"error": "Auditoría no encontrada"}), 404
    return jsonify(registro["resultados"])


@app.route("/descargar-excel/<int:indice>")
@login_required
def descargar_excel_historial(indice):
    try:
        historial = cargar_historial_db()
        registro = historial[indice]
    except (FileNotFoundError, IndexError):
        return "Auditoría no encontrada.", 404
    if registro.get("usuario", "admin") != session["usuario"]:
        return "Auditoría no encontrada.", 404
    wb = openpyxl.Workbook()
    ws = wb.active
    if ws is None:
        return "Error interno al generar el Excel.", 500
    ws.title = "Leads"
    ws.append([
        "Nombre", "Direccion", "Telefono", "Web", "Rating", "Resenas",
        "Score", "Clasificacion", "Servicios recomendados"
    ])
    for r in registro["resultados"]:
        ws.append([
            r["nombre"], r["direccion"], r["telefono"], r["web"],
            r["rating"], r["cantidad_resenas"], r["score"], r["clasificacion"],
            ", ".join(r["servicios"])
        ])
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"leads_{registro['tipo']}_{registro['ciudad']}.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@app.route("/clientes", methods=["GET", "POST"])
@login_required
def clientes():
    usuario = session["usuario"]
    registro_usuario = cargar_auth().get(usuario)
    if not plan_permite(registro_usuario, "crm"):
        return jsonify({"error": "El CRM de clientes está disponible en el plan Pro y Agency."}), 403
    try:
        lista = cargar_clientes_db()
    except FileNotFoundError:
        lista = []
    if request.method == "POST":
        nuevo = request.json
        nuevo["estado"] = "contactado"
        nuevo["fecha_agregado"] = datetime.now().strftime("%d/%m/%Y")
        nuevo["usuario"] = usuario
        lista.insert(0, nuevo)
        guardar_clientes_db(lista)
        return jsonify({"ok": True})
    return jsonify([c for c in lista if c.get("usuario", "admin") == usuario])


@app.route("/proyectos", methods=["GET", "POST"])
@login_required
def proyectos():
    usuario = session["usuario"]
    try:
        lista = cargar_proyectos_db()
    except FileNotFoundError:
        lista = []
    if request.method == "POST":
        nuevo = request.json
        nuevo["fecha"] = datetime.now().strftime("%d/%m/%Y")
        nuevo["usuario"] = usuario
        lista.insert(0, nuevo)
        guardar_proyectos_db(lista)
        return jsonify({"ok": True})
    return jsonify([p for p in lista if p.get("usuario", "admin") == usuario])


@app.route("/asignar-proyecto", methods=["POST"])
@login_required
def asignar_proyecto():
    datos = request.json
    usuario = session["usuario"]
    try:
        historial = cargar_historial_db()
    except FileNotFoundError:
        historial = []
    indice = datos.get("indice")
    if indice is not None and 0 <= indice < len(historial) and historial[indice].get("usuario", "admin") == usuario:
        historial[indice]["proyecto"] = datos.get("proyecto", "")
        guardar_historial_db(historial)
    return jsonify({"ok": True})


@app.route("/borrar-proyecto", methods=["POST"])
@login_required
def borrar_proyecto():
    nombre = request.json.get("nombre", "")
    usuario = session["usuario"]
    try:
        lista = cargar_proyectos_db()
    except FileNotFoundError:
        lista = []
    lista = [p for p in lista if not (p.get("nombre") == nombre and p.get("usuario", "admin") == usuario)]
    guardar_proyectos_db(lista)
    try:
        historial = cargar_historial_db()
        for a in historial:
            if a.get("proyecto") == nombre and a.get("usuario", "admin") == usuario:
                a["proyecto"] = ""
        guardar_historial_db(historial)
    except FileNotFoundError:
        pass
    return jsonify({"ok": True})


@app.route("/clientes/estado", methods=["POST"])
@login_required
def cambiar_estado_cliente():
    datos = request.json
    usuario = session["usuario"]
    try:
        lista = cargar_clientes_db()
    except FileNotFoundError:
        return jsonify({"ok": False}), 404
    for c in lista:
        if c["nombre"] == datos["nombre"] and c.get("usuario", "admin") == usuario:
            c["estado"] = datos["estado"]
    guardar_clientes_db(lista)
    return jsonify({"ok": True})


@app.route("/perfil")
@login_required
def perfil():
    usuario = session["usuario"]
    auth = cargar_auth()
    registro = auth.get(usuario, {})
    try:
        historial = cargar_historial_db()
    except FileNotFoundError:
        historial = []
    try:
        clientes_lista = cargar_clientes_db()
    except FileNotFoundError:
        clientes_lista = []
    try:
        proyectos_lista = cargar_proyectos_db()
    except FileNotFoundError:
        proyectos_lista = []
    return jsonify({
        "usuario": usuario,
        "limite": registro.get("limite"),
        "usadas": registro.get("usadas", 0),
        "auditorias": len([h for h in historial if h.get("usuario", "admin") == usuario]),
        "clientes": len([c for c in clientes_lista if c.get("usuario", "admin") == usuario]),
        "proyectos": len([p for p in proyectos_lista if p.get("usuario", "admin") == usuario])
    })


@app.route("/resumen")
@login_required
def resumen():
    usuario = session["usuario"]
    try:
        clientes_lista = [c for c in cargar_clientes_db() if c.get("usuario", "admin") == usuario]
    except FileNotFoundError:
        clientes_lista = []
    try:
        historial_lista = [h for h in cargar_historial_db() if h.get("usuario", "admin") == usuario]
    except FileNotFoundError:
        historial_lista = []
    facturado_todos = cargar_facturado_db()
    facturado = facturado_todos.get(usuario, {"total": 0, "registrados": {}})
    for c in clientes_lista:
        monto = float(c.get("cerrado_en") or 0)
        clave = c["nombre"]
        anterior = facturado["registrados"].get(clave, 0)
        if monto != anterior:
            facturado["total"] += monto - anterior
            facturado["registrados"][clave] = monto
    facturado_todos[usuario] = facturado
    guardar_facturado_db(facturado_todos)
    return jsonify({
        "facturado": facturado["total"],
        "clientes_activos": len(clientes_lista),
        "auditorias": len(historial_lista),
        "cerrados": len([c for c in clientes_lista if c.get("estado") == "cerrado"]),
        "negociacion": len([c for c in clientes_lista if c.get("estado") == "en negociación"])
    })


@app.route("/clientes/presupuesto", methods=["POST"])
@login_required
def actualizar_presupuesto():
    datos = request.json
    usuario = session["usuario"]
    try:
        lista = cargar_clientes_db()
    except FileNotFoundError:
        return jsonify({"ok": False}), 404
    for c in lista:
        if c["nombre"] == datos["nombre"] and c.get("usuario", "admin") == usuario:
            if "presupuesto" in datos:
                c["presupuesto"] = datos["presupuesto"]
            if "cerrado_en" in datos:
                c["cerrado_en"] = datos["cerrado_en"]
    guardar_clientes_db(lista)
    return jsonify({"ok": True})


@app.route("/clientes/borrar", methods=["POST"])
@login_required
def borrar_cliente():
    datos = request.json
    usuario = session["usuario"]
    try:
        lista = cargar_clientes_db()
    except FileNotFoundError:
        return jsonify({"ok": False}), 404
    if datos.get("todo"):
        lista = [c for c in lista if c.get("usuario", "admin") != usuario]
    else:
        lista = [c for c in lista if not (c["nombre"] == datos["nombre"] and c.get("usuario", "admin") == usuario)]
    guardar_clientes_db(lista)
    return jsonify({"ok": True})


@app.route("/historial/borrar", methods=["POST"])
@login_required
def borrar_historial():
    datos = request.json
    usuario = session["usuario"]
    try:
        lista = cargar_historial_db()
    except FileNotFoundError:
        return jsonify({"ok": False}), 404
    if datos.get("todo"):
        lista = [h for h in lista if h.get("usuario", "admin") != usuario]
    else:
        indice = datos.get("indice")
        if indice is not None and 0 <= indice < len(lista) and lista[indice].get("usuario", "admin") == usuario:
            lista.pop(indice)
    guardar_historial_db(lista)
    return jsonify({"ok": True})


@app.route("/historial")
@login_required
def historial():
    try:
        datos = cargar_historial_db()
    except FileNotFoundError:
        datos = []
    usuario = session["usuario"]
    resumen = [
        {**{k: r[k] for k in ("fecha", "tipo", "ciudad", "zona", "total", "calientes", "tibios", "frios")},
         "proyecto": r.get("proyecto", ""), "indice": i}
        for i, r in enumerate(datos) if r.get("usuario", "admin") == usuario
    ]
    resumen.reverse()
    return jsonify(resumen)


if __name__ == "__main__":
    app.run(debug=True, port=5001)
