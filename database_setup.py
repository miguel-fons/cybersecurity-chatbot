import sqlite3
import os
import hashlib
from config import DB_PATH


def hash_password(password: str) -> str:
    """Devuelve el hash SHA-256 de la contraseña"""
    return hashlib.sha256(password.encode()).hexdigest()


def create_tables():
    """Crea las tablas necesarias y aplica migraciones para agregar columnas faltantes."""
    # Asegurar existencia del directorio de datos
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    # Activar claves foráneas
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    # Crear tabla users (sin department en versiones antiguas)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT CHECK(role IN ('admin', 'user')) NOT NULL DEFAULT 'user'
        )
    ''')

    # Migración: agregar columna department si no existe
    cursor.execute("PRAGMA table_info(users)")
    cols = [row[1] for row in cursor.fetchall()]
    if 'department' not in cols:
        cursor.execute(
            "ALTER TABLE users ADD COLUMN department TEXT NOT NULL DEFAULT 'General'"
        )

    # Crear tabla phishing_scenarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS phishing_scenarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scenario_text TEXT NOT NULL,
            difficulty_level TEXT CHECK(difficulty_level IN ('Fácil', 'Intermedio', 'Difícil')) NOT NULL,
            image_path TEXT
        )
    ''')

    # Crear tabla user_interactions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            scenario_id INTEGER NOT NULL,
            user_response TEXT NOT NULL,
            chatbot_feedback TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(scenario_id) REFERENCES phishing_scenarios(id)
        )
    ''')

    # Crear tabla user_metrics
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_metrics (
            user_id INTEGER PRIMARY KEY,
            scenarios_completed INTEGER DEFAULT 0,
            total_attempts INTEGER DEFAULT 0,
            correct_percentage REAL DEFAULT 0.0,
            error_percentage REAL DEFAULT 0.0,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    # Índices para optimizar
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_user_interactions_user ON user_interactions(user_id)"
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_phishing_scenarios_difficulty ON phishing_scenarios(difficulty_level)"
    )

    # Trigger para actualizar métricas automáticamente
    cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS trg_update_user_metrics
        AFTER INSERT ON user_interactions
        BEGIN
            INSERT OR REPLACE INTO user_metrics (
                user_id,
                scenarios_completed,
                total_attempts,
                correct_percentage,
                error_percentage
            )
            SELECT
                ui.user_id,
                COUNT(DISTINCT ui.scenario_id),
                COUNT(ui.id),
                ROUND(
                    SUM(CASE WHEN ui.chatbot_feedback LIKE '¡Correcto!%' THEN 1 ELSE 0 END) * 100.0 / COUNT(ui.id),
                    2
                ),
                ROUND(
                    SUM(CASE WHEN ui.chatbot_feedback NOT LIKE '¡Correcto!%' THEN 1 ELSE 0 END) * 100.0 / COUNT(ui.id),
                    2
                )
            FROM user_interactions ui
            WHERE ui.user_id = NEW.user_id
            GROUP BY ui.user_id;
        END;
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
            "INSERT INTO users (username, password_hash, role, department) VALUES (?, ?, ?, ?)",
            ("admin", hashed_pw, "admin", "TI")
        )
        print("Usuario administrador creado: admin / admin123 (departamento: TI)")
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
        (
            "Recibes un correo de tu banco indicando actividad sospechosa en tu cuenta. Te piden hacer clic en un enlace.",
            "Fácil",
            "ui/assets/scenario_images/escenario1.png"
        ),
        (
            "Un correo de Recursos Humanos te indica que actualices tu nómina a través de un enlace desconocido.",
            "Intermedio",
            "ui/assets/scenario_images/escenario2.png"
        ),
        (
            "Un alto ejecutivo te solicita transferir dinero a una cuenta desconocida de inmediato.",
            "Difícil",
            "ui/assets/scenario_images/escenario3.png"
        )
    ])

    conn.commit()
    conn.close()
    print("Escenarios de prueba insertados correctamente.")


def get_random_phishing_scenario():
    """Obtiene un escenario de phishing aleatorio."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, scenario_text, difficulty_level, image_path FROM phishing_scenarios ORDER BY RANDOM() LIMIT 1"
    )
    scenario = cursor.fetchone()
    conn.close()
    return {
        "id": scenario[0],
        "text": scenario[1],
        "difficulty": scenario[2],
        "image": scenario[3]
    } if scenario else None


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


def get_user_stats(user_id):
    """Obtiene estadísticas agregadas para un usuario a partir de user_interactions."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        '''
        SELECT
            COUNT(DISTINCT scenario_id) AS completed,
            COUNT(*) AS total,
            SUM(CASE WHEN chatbot_feedback LIKE '¡Correcto!%' THEN 1 ELSE 0 END) AS correct,
            MAX(timestamp) AS last_active
        FROM user_interactions
        WHERE user_id = ?
        ''',
        (user_id,)
    )

    result = cursor.fetchone()
    conn.close()

    if not result or result[1] == 0:
        return None

    completed, total, correct, last_active = result
    correct = correct or 0
    accuracy = round((correct / total) * 100, 2) if total else 0.0

    return {
        "completed": completed,
        "accuracy": accuracy,
        "last_active": last_active,
        "score": correct,
    }


# Inicializar base de datos (migración incluida)
if __name__ == "__main__":
    create_tables()
    insert_default_admin()
    insert_sample_scenarios()
    print("Base de datos lista.")
