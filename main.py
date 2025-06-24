import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from ui.onboarding_window import OnboardingWindow
from ui.login_window import LoginWindow
from ui.main_window import ChatWindow
from ui.admin_window import AdminWindow

def main():
    app = QApplication(sys.argv)

    # Lista para mantener vivas las ventanas
    windows = []

    # Mostrar Onboarding
    onboarding = OnboardingWindow()

    def on_start():
        # Al hacer clic en "Comenzar", ocultamos onboarding y lanzamos login
        onboarding.hide()

        login_win = LoginWindow()
        windows.append(login_win)

        def on_login(username: str, role: str):
            # Ocultar login
            login_win.hide()

            # Abrir ventana según rol
            if role == "admin":
                win = AdminWindow()
            else:
                win = ChatWindow(username)
            windows.append(win)
            win.show()

        # Conectar señal de login y mostrar ventana de login
        login_win.login_success.connect(on_login)
        login_win.show()

    # Conectar señal de inicio y mostrar onboarding
    onboarding.start_clicked.connect(on_start)
    onboarding.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
