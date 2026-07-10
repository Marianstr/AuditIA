import json
import shutil
from datetime import datetime
from werkzeug.security import generate_password_hash

AUTH_FILE = "auth.json"

def ya_hasheada(password):
    return password.startswith("pbkdf2:") or password.startswith("scrypt:")

def main():
    backup = f"{AUTH_FILE}.bak-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    shutil.copy(AUTH_FILE, backup)
    print(f"Backup creado en {backup}")

    with open(AUTH_FILE, "r", encoding="utf-8") as f:
        datos = json.load(f)

    migrados = 0
    for usuario, registro in datos.items():
        password = registro.get("password", "")
        if ya_hasheada(password):
            continue
        registro["password"] = generate_password_hash(password, method="pbkdf2:sha256")
        migrados += 1

    with open(AUTH_FILE, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)

    print(f"Contraseñas migradas: {migrados} de {len(datos)}")

if __name__ == "__main__":
    main()
