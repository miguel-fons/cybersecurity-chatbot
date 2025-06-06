import os
from dotenv import load_dotenv
from openai import OpenAI

# Cargar las variables de entorno del archivo .env
load_dotenv()

# Configuración de la API de OpenAI
MODEL_NAME = "gpt-4o-mini"
MAX_TOKENS = 200
TEMPERATURE = 0.7
API_KEY = os.getenv("OPENAI_API_KEY")  # Cargar la clave API desde el .env

# Ruta raíz del proyecto
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Ruta absoluta al archivo de la base de datos
DB_PATH = os.path.join(BASE_DIR, "data", "chatbot.db")