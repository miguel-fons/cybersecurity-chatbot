import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QComboBox, QMessageBox, QHBoxLayout, QGroupBox, QDialog,
    QLineEdit, QFormLayout
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from auth import get_all_users, delete_user, register_user
from utils.csv_exporter import export_user_stats_to_csv
from database_setup import get_user_stats

class RegisterEmployeeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Registrar Empleado")
        self.setGeometry(400, 250, 300, 200)
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout(self)

        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Usuario")
        layout.addRow("Usuario:", self.user_input)

        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Contraseña (mínimo de 6 caracteres)")
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addRow("Contraseña:", self.pass_input)

        self.dept_input = QLineEdit()
        self.dept_input.setPlaceholderText("Departamento")
        layout.addRow("Departamento:", self.dept_input)

        btn_layout = QHBoxLayout()
        self.register_btn = QPushButton("Registrar")
        self.register_btn.clicked.connect(self.register_employee)
        btn_layout.addWidget(self.register_btn)

        self.cancel_btn = QPushButton("Cancelar")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)

        layout.addRow(btn_layout)

    def register_employee(self):
        usuario = self.user_input.text().strip()
        password = self.pass_input.text()
        dept = self.dept_input.text().strip()
        if not usuario or not password or not dept:
            QMessageBox.warning(self, "Error", "Todos los campos son obligatorios.")
            return
        if len(password) < 6:
            QMessageBox.warning(self, "Error", "La contraseña debe tener al menos 6 caracteres.")
            return

        result = register_user(usuario, password, dept)
        if "exitosamente" in result:
            QMessageBox.information(self, "Éxito", result)
            self.accept()
        else:
            QMessageBox.warning(self, "Error", result)

class AdminWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Panel del Administrador")
        self.setGeometry(300, 200, 500, 450)

        self.setStyleSheet("""
            QWidget {
                background-color: #F4F4F4;
                color: black;
            }
            QLabel {
                font-size: 14px;
            }
            QGroupBox {
                font-size: 14px;
                color: black;
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
            QMessageBox QLabel {
                color: black;
            }
            QMessageBox QPushButton {
                color: black;
            }
        """ )

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

        self.add_button = QPushButton("Agregar empleado")
        self.add_button.clicked.connect(self.open_register_dialog)
        buttons_layout.addWidget(self.add_button)

        self.export_button = QPushButton("Exportar CSV")
        self.export_button.clicked.connect(self.export_csv)
        buttons_layout.addWidget(self.export_button)

        self.delete_button = QPushButton("Eliminar usuario")
        self.delete_button.clicked.connect(self.confirm_delete)
        buttons_layout.addWidget(self.delete_button)

        layout.addLayout(buttons_layout)
        self.setLayout(layout)

        if self.user_selector.count() > 0:
            self.display_user_stats()

    def refresh_user_list(self):
        self.user_selector.clear()
        users = get_all_users()
        for user in users:
            self.user_selector.addItem(user[1], user[0])

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

    def open_register_dialog(self):
        dialog = RegisterEmployeeDialog(self)
        if dialog.exec():
            self.refresh_user_list()

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
