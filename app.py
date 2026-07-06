from flask import Flask, render_template, request, jsonify, send_file
from dotenv import load_dotenv
import os
import json
from datetime import datetime
import io
import openpyxl

load_dotenv()

from scraper import buscar_negocios_google
from scoring.lead_scorer import calcular_score, clasificar_lead, recomendar_servicios

app = Flask(__name__)

# Guardamos la última búsqueda en memoria para poder exportarla a Excel
ultima_busqueda = {"resultados": [], "tipo": "", "ciudad": ""}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/buscar", methods=["POST"])
def buscar():
    tipo = request.json.get("tipo")
    ciudad = request.json.get("ciudad")
    zona = request.json.get("zona")
    
    negocios = buscar_negocios_google(tipo, ciudad, zona)
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
        "tipo": tipo,
        "ciudad": ciudad,
        "zona": zona or "",
        "total": len(resultados),
        "calientes": len([r for r in resultados if r["clasificacion"] == "caliente"]),
        "tibios": len([r for r in resultados if r["clasificacion"] == "tibio"]),
        "frios": len([r for r in resultados if r["clasificacion"] == "frio"]),
        "resultados": resultados
    }
    try:
        with open("historial.json", "r", encoding="utf-8") as f:
            historial = json.load(f)
    except FileNotFoundError:
        historial = []
    historial.insert(0, registro)
    with open("historial.json", "w", encoding="utf-8") as f:
        json.dump(historial, f, ensure_ascii=False, indent=2)
    ultima_busqueda["resultados"] = resultados
    ultima_busqueda["tipo"] = tipo
    ultima_busqueda["ciudad"] = ciudad
    return jsonify(resultados)

@app.route("/descargar-excel/<int:indice>")
def descargar_excel_historial(indice):
    try:
        with open("historial.json", "r", encoding="utf-8") as f:
            historial = json.load(f)
        registro = historial[indice]
    except (FileNotFoundError, IndexError):
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
def clientes():
    try:
        with open("clientes.json", "r", encoding="utf-8") as f:
            lista = json.load(f)
    except FileNotFoundError:
        lista = []
    if request.method == "POST":
        nuevo = request.json
        nuevo["estado"] = "contactado"
        nuevo["fecha_agregado"] = datetime.now().strftime("%d/%m/%Y")
        lista.insert(0, nuevo)
        with open("clientes.json", "w", encoding="utf-8") as f:
            json.dump(lista, f, ensure_ascii=False, indent=2)
        return jsonify({"ok": True})
    return jsonify(lista)


@app.route("/clientes/estado", methods=["POST"])
def cambiar_estado_cliente():
    datos = request.json
    try:
        with open("clientes.json", "r", encoding="utf-8") as f:
            lista = json.load(f)
    except FileNotFoundError:
        return jsonify({"ok": False}), 404
    for c in lista:
        if c["nombre"] == datos["nombre"]:
            c["estado"] = datos["estado"]
    with open("clientes.json", "w", encoding="utf-8") as f:
        json.dump(lista, f, ensure_ascii=False, indent=2)
    return jsonify({"ok": True})
@app.route("/resumen")
def resumen():
    try:
        with open("clientes.json", "r", encoding="utf-8") as f:
            clientes_lista = json.load(f)
    except FileNotFoundError:
        clientes_lista = []
    try:
        with open("historial.json", "r", encoding="utf-8") as f:
            historial_lista = json.load(f)
    except FileNotFoundError:
        historial_lista = []
    try:
        with open("facturado.json", "r", encoding="utf-8") as f:
            facturado = json.load(f)
    except FileNotFoundError:
        facturado = {"total": 0, "registrados": {}}
    for c in clientes_lista:
        monto = float(c.get("cerrado_en") or 0)
        clave = c["nombre"]
        anterior = facturado["registrados"].get(clave, 0)
        if monto != anterior:
            facturado["total"] += monto - anterior
            facturado["registrados"][clave] = monto
    with open("facturado.json", "w", encoding="utf-8") as f:
        json.dump(facturado, f, ensure_ascii=False, indent=2)
    return jsonify({
        "facturado": facturado["total"],
        "clientes_activos": len(clientes_lista),
        "auditorias": len(historial_lista),
        "cerrados": len([c for c in clientes_lista if c.get("estado") == "cerrado"]),
        "negociacion": len([c for c in clientes_lista if c.get("estado") == "en negociación"])
    })
@app.route("/clientes/presupuesto", methods=["POST"])
def actualizar_presupuesto():
    datos = request.json
    try:
        with open("clientes.json", "r", encoding="utf-8") as f:
            lista = json.load(f)
    except FileNotFoundError:
        return jsonify({"ok": False}), 404
    for c in lista:
        if c["nombre"] == datos["nombre"]:
            if "presupuesto" in datos:
                c["presupuesto"] = datos["presupuesto"]
            if "cerrado_en" in datos:
                c["cerrado_en"] = datos["cerrado_en"]
    with open("clientes.json", "w", encoding="utf-8") as f:
        json.dump(lista, f, ensure_ascii=False, indent=2)
    return jsonify({"ok": True})
@app.route("/clientes/borrar", methods=["POST"])
def borrar_cliente():
    datos = request.json
    try:
        with open("clientes.json", "r", encoding="utf-8") as f:
            lista = json.load(f)
    except FileNotFoundError:
        return jsonify({"ok": False}), 404
    if datos.get("todo"):
        lista = []
    else:
        lista = [c for c in lista if c["nombre"] != datos["nombre"]]
    with open("clientes.json", "w", encoding="utf-8") as f:
        json.dump(lista, f, ensure_ascii=False, indent=2)
    return jsonify({"ok": True})


@app.route("/historial/borrar", methods=["POST"])
def borrar_historial():
    datos = request.json
    try:
        with open("historial.json", "r", encoding="utf-8") as f:
            lista = json.load(f)
    except FileNotFoundError:
        return jsonify({"ok": False}), 404
    if datos.get("todo"):
        lista = []
    else:
        indice = datos.get("indice")
        if indice is not None and 0 <= indice < len(lista):
            lista.pop(indice)
    with open("historial.json", "w", encoding="utf-8") as f:
        json.dump(lista, f, ensure_ascii=False, indent=2)
    return jsonify({"ok": True})
@app.route("/historial")
def historial():
    try:
        with open("historial.json", "r", encoding="utf-8") as f:
            datos = json.load(f)
    except FileNotFoundError:
        datos = []
    resumen = [{k: r[k] for k in ("fecha", "tipo", "ciudad", "zona", "total", "calientes", "tibios", "frios")} for r in datos]
    return jsonify(resumen)
@app.route("/descargar-excel")
def descargar_excel():
    resultados = ultima_busqueda["resultados"]
    if not resultados:
        return "No hay resultados para exportar. Hacé una búsqueda primero.", 400
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Leads"
    ws.append(["Nombre", "Direccion", "Telefono", "Web", "Rating", "Resenas", "Score", "Clasificacion", "Servicios recomendados"])
    for r in resultados:
        ws.append([
            r["nombre"],
            r["direccion"],
            r["telefono"],
            r["web"],
            r["rating"],
            r["cantidad_resenas"],
            r["score"],
            r["clasificacion"],
            ", ".join(r["servicios"])
        ])
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    nombre_archivo = f"leads_{ultima_busqueda['tipo']}_{ultima_busqueda['ciudad']}.xlsx"
    return send_file(
        buffer,
        as_attachment=True,
        download_name=nombre_archivo,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

if __name__ == "__main__":
    app.run(debug=True, port=5001)