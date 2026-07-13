import os
import psycopg2

def get_connection():
    """
    Abre una conexión a la base de datos Postgres usando la variable
    de entorno DATABASE_URL (configurada en Render).
    """
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise Exception("No se encontró la variable DATABASE_URL")
    conn = psycopg2.connect(database_url)
    return conn

def crear_tabla_usuarios():
    """
    Crea la tabla 'usuarios' en Postgres si todavía no existe.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            limite INTEGER,
            usadas INTEGER DEFAULT 0,
            plan TEXT DEFAULT 'free'
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

def cargar_auth_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT username, password, limite, usadas, plan FROM usuarios")
    filas = cur.fetchall()
    cur.close()
    conn.close()
    datos = {}
    for username, password, limite, usadas, plan in filas:
        datos[username] = {"password": password, "limite": limite, "usadas": usadas, "plan": plan}
    return datos

def guardar_auth_db(datos):
    conn = get_connection()
    cur = conn.cursor()
    for username, info in datos.items():
        cur.execute("""
            INSERT INTO usuarios (username, password, limite, usadas, plan)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (username) DO UPDATE SET
                password = EXCLUDED.password,
                limite = EXCLUDED.limite,
                usadas = EXCLUDED.usadas,
                plan = EXCLUDED.plan
        """, (username, info["password"], info.get("limite"), info.get("usadas", 0), info.get("plan", "free")))
    conn.commit()
    cur.close()
    conn.close()
