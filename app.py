from flask import Flask, render_template, request, jsonify, send_file
from dotenv import load_dotenv
import os
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
    ultima_busqueda["resultados"] = resultados
    ultima_busqueda["tipo"] = tipo
    ultima_busqueda["ciudad"] = ciudad
    return jsonify(resultados)

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