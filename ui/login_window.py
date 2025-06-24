import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QHBoxLayout, QMessageBox
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, pyqtSignal

# Importa función de login
try:
    from auth import login_user
except ImportError:
    # Función dummy para pruebas básicas
    def login_user(username: str, password: str) -> dict:
        if username == "example" and password == "secret123":
            return {"success": True, "user_id": 1, "role": "admin"}
        return {"success": False, "message": "Usuario o contraseña incorrectos."}

class LoginWindow(QWidget):
    # Señal que emite (username, role) al iniciar sesión correctamente
    login_success = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Iniciar Sesión")
        self.setGeometry(400, 200, 350, 200)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)

        title = QLabel("Bienvenido a Chatbot Phishing")
        title.setFont(QFont("Arial", 16, weight=QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Nombre de usuario")
        layout.addWidget(self.user_input)

        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Contraseña")
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.pass_input)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red;")
        layout.addWidget(self.error_label)

        btn_layout = QHBoxLayout()

        self.login_btn = QPushButton("Iniciar Sesión")
        self.login_btn.clicked.connect(self.handle_login)
        btn_layout.addWidget(self.login_btn)

        self.forgot_btn = QPushButton("¿Olvidaste tu contraseña?")
        self.forgot_btn.clicked.connect(self.handle_forgot)
        btn_layout.addWidget(self.forgot_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def handle_login(self):
        username = self.user_input.text().strip()
        password = self.pass_input.text()

        if not username or not password:
            self.error_label.setText("Ambos campos son obligatorios.")
            return
        if len(password) < 6:
            self.error_label.setText("La contraseña debe tener al menos 6 caracteres.")
            return

        result = login_user(username, password)
        if result.get("success"):
            # Emitimos señal y cerramos login
            self.login_success.emit(username, result.get("role"))
            self.close()
        else:
            self.error_label.setText(result.get("message", "Error de autenticación."))

    def handle_forgot(self):
        QMessageBox.information(
            self,
            "¿Olvidaste tu contraseña?",
            "Funcionalidad no implementada. Contacta al administrador."
        )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = LoginWindow()
    win.show()
    sys.exit(app.exec())
