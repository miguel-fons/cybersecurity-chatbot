import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QMessageBox, QScrollArea
)
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import Qt

from chatbot import get_chatbot_response, get_new_scenario
from auth import get_user_id

# ----- Configuración base -----
COLOR_PRIMARY = "#47436B"
TEXT_COLOR = "#FFFFFF"
MAX_INTERACTIONS_PER_SCENARIO = 3

class ChatWindow(QWidget):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.user_id = get_user_id(username)
        self.interaction_count = 0
        self.scenario = get_new_scenario()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Chat de Capacitación en Phishing")
        self.setStyleSheet(f"background-color: {COLOR_PRIMARY}; color: {TEXT_COLOR};")
        self.setMinimumSize(850, 650)

        # Escenario
        self.scenario_label = QLabel(self.scenario['text'])
        self.scenario_label.setWordWrap(True)
        self.scenario_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.scenario_label.setStyleSheet("margin-bottom: 10px;")

        # Imagen del escenario
        self.image_label = QLabel()
        pixmap = QPixmap(self.scenario['image'])
        self.image_label.setPixmap(pixmap.scaledToWidth(600, Qt.TransformationMode.SmoothTransformation))
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Área de conversación
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.setStyleSheet("background-color: #FFFFFF; color: #000000;")

        # Entrada de texto
        self.input_line = QLineEdit()
        self.input_line.setPlaceholderText("Escribe tu respuesta aquí...")
        self.input_line.returnPressed.connect(self.handle_send)

        # Botón de enviar
        self.send_button = QPushButton("Enviar")
        self.send_button.clicked.connect(self.handle_send)

        # Layouts
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.scenario_label)
        main_layout.addWidget(self.image_label)
        main_layout.addWidget(self.chat_area)

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.input_line)
        input_layout.addWidget(self.send_button)

        main_layout.addLayout(input_layout)
        self.setLayout(main_layout)

    def handle_send(self):
        user_text = self.input_line.text().strip()
        if not user_text:
            return

        self.chat_area.append(f"<b>Tú:</b> {user_text}")
        self.input_line.clear()

        # Obtener respuesta del chatbot
        bot_response = get_chatbot_response(self.user_id, self.scenario, user_text)
        self.chat_area.append(f"<b>Chatbot:</b> {bot_response}")

        self.interaction_count += 1
        if self.interaction_count >= MAX_INTERACTIONS_PER_SCENARIO or "Has completado este escenario" in bot_response:
            self.load_new_scenario()

    def load_new_scenario(self):
        self.interaction_count = 0
        self.scenario = get_new_scenario()
        if not self.scenario:
            QMessageBox.information(self, "Fin", "No hay más escenarios disponibles.")
            self.close()
            return

        self.scenario_label.setText(self.scenario['text'])
        pixmap = QPixmap(self.scenario['image'])
        self.image_label.setPixmap(pixmap.scaledToWidth(600, Qt.TransformationMode.SmoothTransformation))
        self.chat_area.append("<i>Nuevo escenario cargado.</i>")

# ----------- Ejecución -----------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    username = input("Ingresa tu nombre de usuario: ")  # Podremos reemplazar esto luego con una interfaz de login
    window = ChatWindow(username)
    window.show()
    sys.exit(app.exec())
