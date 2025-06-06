import sqlite3
import csv
from auth import hash_password, user_exists, count_total_users
from config import DB_PATH

USER_LIMIT = 50

def get_all_users():
    """Retorna una lista de todos los usuarios que NO son administradores."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM users WHERE role = 'user'")
    users = cursor.fetchall()
    conn.close()
    return users

def get_user_metrics(user_id):
    """Retorna las métricas completas de un usuario específico."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT u.username, m.scenarios_completed, m.total_attempts,
               m.correct_percentage, m.error_percentage
        FROM users u
        LEFT JOIN user_metrics m ON u.id = m.user_id
        WHERE u.id = ?
    ''', (user_id,))
    data = cursor.fetchone()
    conn.close()
    return data  # Puede ser None si el usuario no tiene métricas aún

def get_all_metrics():
    """Retorna una lista con las métricas de todos los usuarios (para graficar o exportar)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT u.id, u.username,
               m.scenarios_completed, m.total_attempts,
               m.correct_percentage, m.error_percentage
        FROM users u
        LEFT JOIN user_metrics m ON u.id = m.user_id
        WHERE u.role = 'user'
    ''')
    results = cursor.fetchall()
    conn.close()
    return results

def export_metrics_to_csv(file_path):
    """Exporta todos los datos de métricas a un archivo CSV."""
    data = get_all_metrics()
    headers = [
        "ID", "Nombre de Usuario",
        "Escenarios Completados", "Escenarios Intentados",
        "Porcentaje de Aciertos", "Porcentaje de Errores"
    ]
    try:
        with open(file_path, mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            for row in data:
                writer.writerow(row)
        return True
    except Exception as e:
        print(f"Error al exportar CSV: {e}")
        return False

def create_user_admin_view(username: str, password: str) -> str:
    """Permite al administrador crear nuevos usuarios desde su panel."""
    if user_exists(username):
        return "Este nombre de usuario ya existe."
    if count_total_users() >= USER_LIMIT:
        return "Se ha alcanzado el límite de usuarios."

    hashed_pw = hash_password(password)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
        (username, hashed_pw, "user")
    )
    conn.commit()
    conn.close()
    return "Usuario creado exitosamente."

def delete_user_by_admin(user_id: int) -> bool:
    """Elimina completamente al usuario, solo si no es el admin."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT role FROM users WHERE id = ?", (user_id,))
    result = cursor.fetchone()

    if not result or result[0] == "admin":
        conn.close()
        return False  # No eliminar si es admin o no existe

    cursor.execute("DELETE FROM user_interactions WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM user_metrics WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return True
