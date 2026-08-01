from dotenv import load_dotenv
load_dotenv()
from db import (
    get_connection,
    cargar_historial_db, guardar_historial_db,
    cargar_clientes_db, guardar_clientes_db,
    cargar_proyectos_db, guardar_proyectos_db,
    cargar_facturado_db, guardar_facturado_db,
)

email = input("Pegá acá el email que querés borrar: ").strip()

# 1. Tabla usuarios
conn = get_connection()
cur = conn.cursor()
cur.execute("DELETE FROM usuarios WHERE username = %s", (email,))
conn.commit()
borrado_usuario = cur.rowcount > 0
cur.close()
conn.close()
print(f"✅ usuarios: borrado {email}" if borrado_usuario else "⚠️ usuarios: no se encontró ese usuario")

# 2. Historial (lista JSONB, entradas con "usuario" == email)
historial = cargar_historial_db()
nuevo_historial = [h for h in historial if h.get("usuario", "admin") != email]
if len(nuevo_historial) != len(historial):
    guardar_historial_db(nuevo_historial)
print(f"✅ historial: {len(historial) - len(nuevo_historial)} registro(s) eliminado(s)")

# 3. Clientes (lista JSONB, entradas con "usuario" == email)
clientes = cargar_clientes_db()
nuevos_clientes = [c for c in clientes if c.get("usuario", "admin") != email]
if len(nuevos_clientes) != len(clientes):
    guardar_clientes_db(nuevos_clientes)
print(f"✅ clientes: {len(clientes) - len(nuevos_clientes)} registro(s) eliminado(s)")

# 4. Proyectos (lista JSONB, entradas con "usuario" == email)
proyectos = cargar_proyectos_db()
nuevos_proyectos = [p for p in proyectos if p.get("usuario", "admin") != email]
if len(nuevos_proyectos) != len(proyectos):
    guardar_proyectos_db(nuevos_proyectos)
print(f"✅ proyectos: {len(proyectos) - len(nuevos_proyectos)} registro(s) eliminado(s)")

# 5. Facturado (dict JSONB, clave == email)
facturado = cargar_facturado_db()
if email in facturado:
    del facturado[email]
    guardar_facturado_db(facturado)
    print(f"✅ facturado: registro eliminado")
else:
    print("⚠️ facturado: no había registro para ese usuario")
