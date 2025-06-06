import sys
import os

# Ajuste de ruta base
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from auth import login_user
from ui.main_window import ChatWindow
# from ui.admin_window import AdminWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)

    username = input("Ingresa tu nombre de usuario: ")
    password = input("Ingresa tu contraseña: ")

    login = login_user(username, password)
    if not login["success"]:
        print("❌", login["message"])
        sys.exit()

    if login["role"] == "admin":
        # window = AdminWindow()
        print("Hola")
    else:
        window = ChatWindow(username)

    window.show()
    sys.exit(app.exec())
