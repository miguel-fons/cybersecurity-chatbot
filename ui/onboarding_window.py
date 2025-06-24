import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QPushButton, QHBoxLayout
)
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt, pyqtSignal

class OnboardingWindow(QWidget):
    # Señal que emite cuando el usuario elige comenzar el flujo
    start_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bienvenida a Chatbot Phishing")
        self.setGeometry(350, 150, 600, 400)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Logo o imagen superior (opcional)
        logo = QLabel()
        pixmap = QPixmap()  # Aquí podrías cargar tu logo: pixmap.load("ruta/logo.png")
        if not pixmap.isNull():
            logo.setPixmap(pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio))
            logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(logo)

        # Título
        title = QLabel("Bienvenido a Chatbot Phishing")
        title.setFont(QFont("Arial", 18, weight=QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Descripción concisa
        desc = QLabel(
            "Entrena a tus empleados en la detección y prevención de ataques de phishing."
            "\nRecibe escenarios reales, feedback adaptativo y estadísticas claras por departamento."
        )
        desc.setWordWrap(True)
        desc.setFont(QFont("Arial", 12))
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc)

        # Botones
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(40)

        start_btn = QPushButton("Comenzar")
        start_btn.setFixedWidth(120)
        start_btn.clicked.connect(self.handle_start)
        btn_layout.addWidget(start_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        exit_btn = QPushButton("Salir")
        exit_btn.setFixedWidth(120)
        exit_btn.clicked.connect(self.close)
        btn_layout.addWidget(exit_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def handle_start(self):
        # Emitir señal y cerrar onboarding
        self.start_clicked.emit()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = OnboardingWindow()
    win.show()
    sys.exit(app.exec())
