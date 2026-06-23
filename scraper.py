import requests
import openpyxl
import os
from scoring.lead_scorer import calcular_score, clasificar_lead

API_KEY = os.environ.get("AIzaSyAtvhaqWe9FIlFBrigdHLGmCBI-2BmJWDE")

def buscar_negocios_google(tipo, ciudad, limite=50):
    print(f"🔍 Buscando {tipo} en {ciudad}...")
    
    negocios = []
    url = "https://places.googleapis.com/v1/places:searchText"
    
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": API_KEY,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.nationalPhoneNumber,places.websiteUri,places.rating,places.userRatingCount"
    }
    
    data = {
        "textQuery": f"{tipo} en {ciudad}",
        "maxResultCount": limite,
        "languageCode": "es"
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code != 200:
        print(f"Error: {response.status_code} — {response.text}")
        return []
    
    lugares = response.json().get("places", [])
    
    for lugar in lugares:
        nombre = lugar.get("displayName", {}).get("text", "Sin nombre")
        tiene_web = "websiteUri" in lugar
        tiene_reseñas = lugar.get("userRatingCount", 0) > 5
        
        negocios.append({
            "nombre": nombre,
            "direccion": lugar.get("formattedAddress", "Sin dirección"),
            "telefono": lugar.get("nationalPhoneNumber", "No disponible"),
            "web": lugar.get("websiteUri", "No tiene"),
            "rating": lugar.get("rating", 0),
            "tiene_sitio_web": tiene_web,
            "tiene_redes_sociales": False,
            "tiene_google_business": True,
            "empleados": 3,
            "tiene_reseñas": tiene_reseñas
        })
    
    return negocios


def generar_excel(negocios, tipo, ciudad):
    archivo = f"leads_{tipo}_{ciudad}.xlsx"
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Leads"

    ws.append(["Nombre", "Dirección", "Teléfono", "Web", "Rating", "Score", "Clasificación"])

    negocios_scored = []
    for negocio in negocios:
        score = calcular_score(negocio)
        clasificacion = clasificar_lead(score)
        negocios_scored.append((negocio, score, clasificacion))

    negocios_scored.sort(key=lambda x: x[1], reverse=True)

    for negocio, score, clasificacion in negocios_scored:
        ws.append([
            negocio["nombre"],
            negocio["direccion"],
            negocio["telefono"],
            negocio["web"],
            negocio["rating"],
            score,
            clasificacion
        ])

    wb.save(archivo)
    print(f"\n✅ Excel generado: {archivo}")
    print(f"✅ Total leads encontrados: {len(negocios)}")
    print("\n📊 Top 10:")
    for negocio, score, clasificacion in negocios_scored[:10]:
        print(f"  {clasificacion.upper():8} ({score} pts) — {negocio['nombre']}")


if __name__ == "__main__":
    print("🔍 AuditIA — Buscando negocios reales con Google Maps\n")
    tipo = input("Tipo de negocio (ej: restaurantes, peluquerías, talleres): ")
    ciudad = input("Ciudad (ej: Madrid, Barcelona): ")
    negocios = buscar_negocios_google(tipo, ciudad)
    if negocios:
        generar_excel(negocios, tipo, ciudad)
    else:
        print("No se encontraron negocios.")
