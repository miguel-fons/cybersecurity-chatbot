import sqlite3
import csv
import os
from datetime import datetime

from config import DB_PATH

def export_user_stats_to_csv():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT 
            u.username,
            COUNT(ui.id) as total_respondidos,
            SUM(CASE WHEN ui.chatbot_feedback LIKE '¡Correcto!%' THEN 1 ELSE 0 END) as respuestas_correctas,
            ROUND(100.0 * SUM(CASE WHEN ui.chatbot_feedback LIKE '¡Correcto!%' THEN 1 ELSE 0 END) / COUNT(ui.id), 2) as porcentaje_aciertos
        FROM users u
        LEFT JOIN user_interactions ui ON u.id = ui.user_id
        GROUP BY u.id
    ''')

    rows = cursor.fetchall()
    conn.close()

    # Asegurar carpeta de exportaciones
    export_dir = "exports"
    os.makedirs(export_dir, exist_ok=True)

    filename = os.path.join(export_dir, f"estadisticas_usuarios_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")

    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Usuario", "Escenarios respondidos", "Respuestas correctas", "Porcentaje de aciertos (%)"])
        writer.writerows(rows)

    return filename
