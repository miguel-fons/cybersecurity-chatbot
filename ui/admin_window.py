import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QComboBox, QMessageBox, QHBoxLayout, QGroupBox
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

# Importaciones relativas
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from auth import get_all_users, delete_user
from utils.csv_exporter import export_user_stats_to_csv
from database_setup import get_user_stats

class AdminWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Panel del Administrador")
        self.setGeometry(300, 200, 500, 400)

        self.setStyleSheet("""
            QWidget {
                background-color: #F4F4F4;
            }
            QLabel {
                font-size: 14px;
            }
            QComboBox, QPushButton {
                padding: 6px;
                font-size: 14px;
            }
            QPushButton {
                background-color: #47436B;
                color: white;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #5E5A85;
            }
        """)

        layout = QVBoxLayout()

        title = QLabel("Selecciona un usuario para ver sus estadísticas")
        title.setFont(QFont("Arial", 14, weight=QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        self.user_selector = QComboBox()
        self.refresh_user_list()
        self.user_selector.currentIndexChanged.connect(self.display_user_stats)
        layout.addWidget(self.user_selector)

        self.stats_box = QGroupBox("Estadísticas del Usuario")
        stats_layout = QVBoxLayout()
        self.completed_label = QLabel("Escenarios completados: ")
        self.accuracy_label = QLabel("Porcentaje de aciertos: ")
        self.last_active_label = QLabel("Última actividad: ")
        self.score_label = QLabel("Puntaje acumulado: ")

        stats_layout.addWidget(self.completed_label)
        stats_layout.addWidget(self.accuracy_label)
        stats_layout.addWidget(self.last_active_label)
        stats_layout.addWidget(self.score_label)
        self.stats_box.setLayout(stats_layout)
        layout.addWidget(self.stats_box)

        buttons_layout = QHBoxLayout()

        self.export_button = QPushButton("Exportar CSV")
        self.export_button.clicked.connect(self.export_csv)
        buttons_layout.addWidget(self.export_button)

        self.delete_button = QPushButton("Eliminar usuario")
        self.delete_button.clicked.connect(self.confirm_delete)
        buttons_layout.addWidget(self.delete_button)

        layout.addLayout(buttons_layout)
        self.setLayout(layout)

        # Mostrar datos del primer usuario por defecto
        if self.user_selector.count() > 0:
            self.display_user_stats()

    def refresh_user_list(self):
        self.user_selector.clear()
        users = get_all_users()
        for user in users:
            self.user_selector.addItem(user[1], user[0])  # username, id

    def display_user_stats(self):
        user_id = self.user_selector.currentData()
        if user_id:
            stats = get_user_stats(user_id)
            if stats:
                self.completed_label.setText(f"Escenarios completados: {stats['completed']}")
                self.accuracy_label.setText(f"Porcentaje de aciertos: {stats['accuracy']}%")
                self.last_active_label.setText(f"Última actividad: {stats['last_active']}")
                self.score_label.setText(f"Puntaje acumulado: {stats['score']}")
            else:
                self.completed_label.setText("No hay datos disponibles para este usuario.")

    def export_csv(self):
        export_user_stats_to_csv()
        QMessageBox.information(self, "Éxito", "Datos exportados correctamente.")

    def confirm_delete(self):
        user_id = self.user_selector.currentData()
        username = self.user_selector.currentText()
        if user_id:
            confirm = QMessageBox.question(
                self,
                "Confirmar eliminación",
                f"¿Estás seguro de que deseas eliminar al usuario '{username}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if confirm == QMessageBox.StandardButton.Yes:
                delete_user(user_id)
                QMessageBox.information(self, "Usuario eliminado", f"'{username}' ha sido eliminado.")
                self.refresh_user_list()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AdminWindow()
    window.show()
    sys.exit(app.exec())
