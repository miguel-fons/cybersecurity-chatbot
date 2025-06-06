import sqlite3
import hashlib
from config import DB_PATH

USER_LIMIT = 50

def hash_password(password: str) -> str:
    """Devuelve el hash SHA-256 de una contraseña."""
    return hashlib.sha256(password.encode()).hexdigest()

def user_exists(username: str) -> bool:
    """Verifica si un nombre de usuario ya está registrado."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def count_total_users() -> int:
    """Retorna el número total de usuarios registrados."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    conn.close()
    return count

def register_user(username: str, password: str) -> str:
    """Registra un nuevo usuario con rol 'user'. Retorna mensaje de estado."""
    if user_exists(username):
        return "Este nombre de usuario ya está registrado."

    if count_total_users() >= USER_LIMIT:
        return "Se ha alcanzado el límite máximo de usuarios permitidos."

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    hashed_pw = hash_password(password)

    cursor.execute(
        "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
        (username, hashed_pw, "user")
    )
    conn.commit()
    conn.close()
    return "Usuario registrado exitosamente."

def login_user(username: str, password: str) -> dict:
    """Verifica credenciales. Retorna dict con éxito, user_id y rol."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, password_hash, role FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return {"success": False, "message": "Usuario no encontrado."}

    user_id, stored_hash, role = row
    if hash_password(password) != stored_hash:
        return {"success": False, "message": "Contraseña incorrecta."}

    return {"success": True, "user_id": user_id, "role": role}

def get_user_role(user_id: int) -> str:
    """Devuelve el rol ('admin' o 'user') de un usuario por su ID."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM users WHERE id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def get_user_id(username: str) -> int:
    """Devuelve el ID de usuario a partir de su nombre."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def delete_user(user_id: int) -> bool:
    """Elimina al usuario de todas las tablas. Retorna True si tuvo éxito."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Verificar existencia
    cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
    if not cursor.fetchone():
        conn.close()
        return False

    # Eliminar interacciones y métricas relacionadas
    cursor.execute("DELETE FROM user_interactions WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM user_metrics WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return True

def get_all_users() -> list:
    """Devuelve una lista de todos los usuarios registrados (excluyendo al administrador)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM users WHERE role = 'user'")
    users = cursor.fetchall()
    conn.close()
    return users
