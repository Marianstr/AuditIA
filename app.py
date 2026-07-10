from flask import Flask, render_template, request, jsonify, send_file, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from functools import wraps
import os
import re
import json
from datetime import datetime
import io
import openpyxl

load_dotenv()

from scraper import buscar_negocios_google
from scoring.lead_scorer import calcular_score, clasificar_lead, recomendar_servicios
from scoring.analizador_web import analizar_web

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or "auditia-secret-key-cambiar-en-produccion"

AUTH_FILE = "auth.json"
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def cargar_auth():
    if not os.path.exists(AUTH_FILE):
        datos = {
            "admin": {"password": generate_password_hash("auditia2026", method="pbkdf2:sha256"), "limite": None, "usadas": 0},
            "ariel": {"password": generate_password_hash("utn2026", method="pbkdf2:sha256"), "limite": 10, "usadas": 0},
            "profe2": {"password": generate_password_hash("utn2026", method="pbkdf2:sha256"), "limite": 10, "usadas": 0},
            "visitante": {"password": generate_password_hash("123", method="pbkdf2:sha256"), "limite": 15, "usadas": 0},
        }
        guardar_auth(datos)
        return datos
    with open(AUTH_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def guardar_auth(datos):
    with open(AUTH_FILE, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)

cargar_auth()

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
    return render_template("index.html", usuario=session["usuario"])

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
        with open("historial.json", "r", encoding="utf-8") as f:
            historial = json.load(f)
    except FileNotFoundError:
        historial = []
    historial.append(registro)
    indice = len(historial) - 1
    with open("historial.json", "w", encoding="utf-8") as f:
        json.dump(historial, f, ensure_ascii=False, indent=2)
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

@app.route("/historial/resultados/<int:indice>")
@login_required
def resultados_historial(indice):
    try:
        with open("historial.json", "r", encoding="utf-8") as f:
            historial = json.load(f)
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
        with open("historial.json", "r", encoding="utf-8") as f:
            historial = json.load(f)
        registro = historial[indice]
    except (FileNotFoundError, IndexError):
        return "Auditoría no encontrada.", 404
    if registro.get("usuario", "admin") != session["usuario"]:
        return "Auditoría no encontrada.", 404
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Leads"
    ws.append(["Nombre", "Direccion", "Telefono", "Web", "Rating", "Resenas", "Score", "Clasificacion", "Servicios recomendados"])
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
    try:
        with open("clientes.json", "r", encoding="utf-8") as f:
            lista = json.load(f)
    except FileNotFoundError:
        lista = []
    if request.method == "POST":
        nuevo = request.json
        nuevo["estado"] = "contactado"
        nuevo["fecha_agregado"] = datetime.now().strftime("%d/%m/%Y")
        nuevo["usuario"] = usuario
        lista.insert(0, nuevo)
        with open("clientes.json", "w", encoding="utf-8") as f:
            json.dump(lista, f, ensure_ascii=False, indent=2)
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
        with open("historial.json", "r", encoding="utf-8") as f:
            historial = json.load(f)
    except FileNotFoundError:
        historial = []
    indice = datos.get("indice")
    if indice is not None and 0 <= indice < len(historial) and historial[indice].get("usuario", "admin") == usuario:
        historial[indice]["proyecto"] = datos.get("proyecto", "")
        with open("historial.json", "w", encoding="utf-8") as f:
            json.dump(historial, f, ensure_ascii=False, indent=2)
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
        with open("historial.json", "r", encoding="utf-8") as f:
            historial = json.load(f)
        for a in historial:
            if a.get("proyecto") == nombre and a.get("usuario", "admin") == usuario:
                a["proyecto"] = ""
        with open("historial.json", "w", encoding="utf-8") as f:
            json.dump(historial, f, ensure_ascii=False, indent=2)
    except FileNotFoundError:
        pass
    return jsonify({"ok": True})


@app.route("/clientes/estado", methods=["POST"])
@login_required
def cambiar_estado_cliente():
    datos = request.json
    usuario = session["usuario"]
    try:
        with open("clientes.json", "r", encoding="utf-8") as f:
            lista = json.load(f)
    except FileNotFoundError:
        return jsonify({"ok": False}), 404
    for c in lista:
        if c["nombre"] == datos["nombre"] and c.get("usuario", "admin") == usuario:
            c["estado"] = datos["estado"]
    with open("clientes.json", "w", encoding="utf-8") as f:
        json.dump(lista, f, ensure_ascii=False, indent=2)
    return jsonify({"ok": True})
@app.route("/perfil")
@login_required
def perfil():
    usuario = session["usuario"]
    auth = cargar_auth()
    registro = auth.get(usuario, {})
    try:
        with open("historial.json", "r", encoding="utf-8") as f:
            historial = json.load(f)
    except FileNotFoundError:
        historial = []
    try:
        with open("clientes.json", "r", encoding="utf-8") as f:
            clientes_lista = json.load(f)
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
        with open("clientes.json", "r", encoding="utf-8") as f:
            clientes_lista = [c for c in json.load(f) if c.get("usuario", "admin") == usuario]
    except FileNotFoundError:
        clientes_lista = []
    try:
        with open("historial.json", "r", encoding="utf-8") as f:
            historial_lista = [h for h in json.load(f) if h.get("usuario", "admin") == usuario]
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
        with open("clientes.json", "r", encoding="utf-8") as f:
            lista = json.load(f)
    except FileNotFoundError:
        return jsonify({"ok": False}), 404
    for c in lista:
        if c["nombre"] == datos["nombre"] and c.get("usuario", "admin") == usuario:
            if "presupuesto" in datos:
                c["presupuesto"] = datos["presupuesto"]
            if "cerrado_en" in datos:
                c["cerrado_en"] = datos["cerrado_en"]
    with open("clientes.json", "w", encoding="utf-8") as f:
        json.dump(lista, f, ensure_ascii=False, indent=2)
    return jsonify({"ok": True})
@app.route("/clientes/borrar", methods=["POST"])
@login_required
def borrar_cliente():
    datos = request.json
    usuario = session["usuario"]
    try:
        with open("clientes.json", "r", encoding="utf-8") as f:
            lista = json.load(f)
    except FileNotFoundError:
        return jsonify({"ok": False}), 404
    if datos.get("todo"):
        lista = [c for c in lista if c.get("usuario", "admin") != usuario]
    else:
        lista = [c for c in lista if not (c["nombre"] == datos["nombre"] and c.get("usuario", "admin") == usuario)]
    with open("clientes.json", "w", encoding="utf-8") as f:
        json.dump(lista, f, ensure_ascii=False, indent=2)
    return jsonify({"ok": True})


@app.route("/historial/borrar", methods=["POST"])
@login_required
def borrar_historial():
    datos = request.json
    usuario = session["usuario"]
    try:
        with open("historial.json", "r", encoding="utf-8") as f:
            lista = json.load(f)
    except FileNotFoundError:
        return jsonify({"ok": False}), 404
    if datos.get("todo"):
        lista = [h for h in lista if h.get("usuario", "admin") != usuario]
    else:
        indice = datos.get("indice")
        if indice is not None and 0 <= indice < len(lista) and lista[indice].get("usuario", "admin") == usuario:
            lista.pop(indice)
    with open("historial.json", "w", encoding="utf-8") as f:
        json.dump(lista, f, ensure_ascii=False, indent=2)
    return jsonify({"ok": True})
@app.route("/historial")
@login_required
def historial():
    try:
        with open("historial.json", "r", encoding="utf-8") as f:
            datos = json.load(f)
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