import sqlite3
import os
import hashlib
from config import DB_PATH


def hash_password(password: str) -> str:
    """Devuelve el hash SHA-256 de la contraseña"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_tables():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Tabla de usuarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT CHECK(role IN ('admin', 'user')) NOT NULL DEFAULT 'user'
        )
    ''')

    # Tabla de escenarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS phishing_scenarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scenario_text TEXT NOT NULL,
            difficulty_level TEXT CHECK(difficulty_level IN ('Fácil', 'Intermedio', 'Difícil')) NOT NULL,
            image_path TEXT
        )
    ''')

    # Tabla de interacciones
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            scenario_id INTEGER,
            user_response TEXT NOT NULL,
            chatbot_feedback TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(scenario_id) REFERENCES phishing_scenarios(id)
        )
    ''')

    # Tabla de métricas para exportar
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            scenarios_completed INTEGER DEFAULT 0,
            total_attempts INTEGER DEFAULT 0,
            correct_percentage REAL DEFAULT 0.0,
            error_percentage REAL DEFAULT 0.0,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    conn.commit()
    conn.close()

def insert_default_admin():
    """Inserta un administrador por defecto si no existe."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        hashed_pw = hash_password("admin123")
        cursor.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            ("admin", hashed_pw, "admin")
        )
        print("Usuario administrador creado: admin / admin123")
    else:
        print("Administrador ya existe.")

    conn.commit()
    conn.close()

def insert_sample_scenarios():
    """Inserta escenarios de prueba con dificultad e imagen."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.executemany('''
        INSERT INTO phishing_scenarios (scenario_text, difficulty_level, image_path)
        VALUES (?, ?, ?)
    ''', [
        ("Recibes un correo de tu banco indicando actividad sospechosa en tu cuenta. Te piden hacer clic en un enlace.", "Fácil", "ui/assets/scenario_images/escenario1.png"),
        ("Un correo de Recursos Humanos te indica que actualices tu nómina a través de un enlace desconocido.", "Intermedio", "ui/assets/scenario_images/escenario2.png"),
        ("Un alto ejecutivo te solicita transferir dinero a una cuenta desconocida de inmediato.", "Difícil", "ui/assets/scenario_images/escenario3.png")
    ])

    conn.commit()
    conn.close()
    print("Escenarios de prueba insertados correctamente.")

def get_random_phishing_scenario():
    """Obtiene un escenario de phishing aleatorio."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, scenario_text, image_path FROM phishing_scenarios ORDER BY RANDOM() LIMIT 1")
    scenario = cursor.fetchone()
    conn.close()
    return {"id": scenario[0], "text": scenario[1], "image": scenario[2]} if scenario else None

def save_user_interaction(user_id, scenario_id, user_response, chatbot_feedback):
    """Guarda la interacción del usuario."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO user_interactions (user_id, scenario_id, user_response, chatbot_feedback) VALUES (?, ?, ?, ?)",
        (user_id, scenario_id, user_response, chatbot_feedback)
    )
    conn.commit()
    conn.close()

# Ejecutar creación y datos de prueba
if __name__ == "__main__":
    create_tables()
    insert_default_admin()
    insert_sample_scenarios()
    print("Base de datos lista.")
