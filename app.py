import io
import json
import os
import re
from datetime import datetime
from functools import wraps

import openpyxl
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, send_file, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash

from scraper import buscar_negocios_google
from scoring.lead_scorer import calcular_score, clasificar_lead, recomendar_servicios
from scoring.analizador_web import analizar_web
from generador_propuesta import generar_propuesta
from buscador_fotos import buscar_foto_categoria

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or "auditia-secret-key-cambiar-en-produccion"

AUTH_FILE = "auth.json"
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
from db import cargar_historial_db, guardar_historial_db, crear_tabla_historial
crear_tabla_historial()
from db import cargar_clientes_db, guardar_clientes_db, crear_tabla_clientes
crear_tabla_clientes()


def cargar_auth():
    from db import cargar_auth_db, crear_tabla_usuarios, guardar_auth_db
    crear_tabla_usuarios()
    datos = cargar_auth_db()
    if not datos:
        datos = {
            "admin": {
                "password": generate_password_hash("auditia2026", method="pbkdf2:sha256"),
                "limite": None, "usadas": 0, "plan": "agency",
            },
            "ariel": {
                "password": generate_password_hash("utn2026", method="pbkdf2:sha256"),
                "limite": 10, "usadas": 0, "plan": "pro",
            },
            "profe2": {
                "password": generate_password_hash("utn2026", method="pbkdf2:sha256"),
                "limite": 10, "usadas": 0, "plan": "pro",
            },
            "visitante": {
                "password": generate_password_hash("123", method="pbkdf2:sha256"),
                "limite": 15, "usadas": 0, "plan": "free",
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
            session["usuario"] = usuario
            return redirect(url_for("index"))
        error = "Usuario o contraseña incorrectos"
    return render_template("login.html", error=error)


@app.route("/registro", methods=["GET", "POST"])
def registro():
    error = None
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
            auth[email] = {
                "password": generate_password_hash(password, method="pbkdf2:sha256"),
                "limite": 5,
                "usadas": 0
            }
            guardar_auth(auth)
            session["usuario"] = email
            return redirect(url_for("index"))
    return render_template("registro.html", error=error)


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
            "servicios": servicios
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
        with open("proyectos.json", "r", encoding="utf-8") as f:
            lista = json.load(f)
    except FileNotFoundError:
        lista = []
    if request.method == "POST":
        nuevo = request.json
        nuevo["fecha"] = datetime.now().strftime("%d/%m/%Y")
        nuevo["usuario"] = usuario
        lista.insert(0, nuevo)
        with open("proyectos.json", "w", encoding="utf-8") as f:
            json.dump(lista, f, ensure_ascii=False, indent=2)
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
        with open("proyectos.json", "r", encoding="utf-8") as f:
            lista = json.load(f)
    except FileNotFoundError:
        lista = []
    lista = [p for p in lista if not (p.get("nombre") == nombre and p.get("usuario", "admin") == usuario)]
    with open("proyectos.json", "w", encoding="utf-8") as f:
        json.dump(lista, f, ensure_ascii=False, indent=2)
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
        with open("proyectos.json", "r", encoding="utf-8") as f:
            proyectos_lista = json.load(f)
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
    try:
        with open("facturado.json", "r", encoding="utf-8") as f:
            facturado_todos = json.load(f)
    except FileNotFoundError:
        facturado_todos = {}
    facturado = facturado_todos.get(usuario, {"total": 0, "registrados": {}})
    for c in clientes_lista:
        monto = float(c.get("cerrado_en") or 0)
        clave = c["nombre"]
        anterior = facturado["registrados"].get(clave, 0)
        if monto != anterior:
            facturado["total"] += monto - anterior
            facturado["registrados"][clave] = monto
    facturado_todos[usuario] = facturado
    with open("facturado.json", "w", encoding="utf-8") as f:
        json.dump(facturado_todos, f, ensure_ascii=False, indent=2)
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
