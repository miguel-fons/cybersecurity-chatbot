import random
from openai import OpenAI
from config import API_KEY, MODEL_NAME, MAX_TOKENS, TEMPERATURE
from database_setup import get_random_phishing_scenario, save_user_interaction
from config import DB_PATH

# Instanciar cliente de OpenAI
client = OpenAI(api_key=API_KEY)

# Diccionario para rastrear las interacciones por usuario
user_interaction_count = {}

def get_new_scenario():
    """Obtiene un nuevo escenario aleatorio desde la base de datos."""
    scenario = get_random_phishing_scenario()
    if not scenario:
        return None
    return scenario

def get_chatbot_response(user_id, scenario, user_input):
    """Genera la respuesta del chatbot con retroalimentación ajustada y guía al usuario."""

    # Si el usuario no tiene un contador, inicializarlo
    if user_id not in user_interaction_count:
        user_interaction_count[user_id] = 0

    # Frases de refuerzo positivo
    positive_feedback_phrases = [
        "¡Buena decisión!", 
        "Eso es correcto.", 
        "Bien pensado.", 
        "Esa es una excelente estrategia."
    ]

    # Contar el número de interacciones por usuario
    if user_interaction_count[user_id] >= 3:
        return "¡Excelente! Has completado este escenario. ¿Quieres otro? (Responde 'sí' para continuar o 'salir' para terminar)"

    try:
        # Crear el historial de conversación con el contexto fijo
        conversation_history = [
            {
                "role": "system",
                "content": (
                    "Eres un chatbot especializado en entrenar a usuarios para detectar ataques de phishing. "
                    "Tu tarea es evaluar la respuesta del usuario en el siguiente escenario. "
                    "Si el usuario da una respuesta acertada, confirma su decisión con una breve retroalimentación positiva "
                    "y luego sugiere un paso adicional. No hagas más de 3 preguntas por escenario."
                    "\n\n📌 **Escenario:** " + scenario["text"]
                )
            },
            {"role": "user", "content": user_input}
        ]

        # Llamar a la API de OpenAI
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=conversation_history,
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE
        )

        bot_response = response.choices[0].message.content.strip()

        # Determinar si la respuesta del bot es apropiada para el escenario
        if "?" in bot_response:
            # Solo dar retroalimentación positiva si la respuesta fue correcta
            if "bueno" in bot_response.lower() or "correcto" in bot_response.lower():
                bot_response = f"{random.choice(positive_feedback_phrases)} {bot_response}"
            else:
                # Evitar dar retroalimentación positiva innecesaria
                bot_response = f"{bot_response} ¿Te gustaría que te diera más detalles sobre cómo identificar phishing?"

        # Guardar la interacción
        save_user_interaction(user_id, scenario["id"], user_input, bot_response)

        # Incrementar el contador de interacciones
        user_interaction_count[user_id] += 1

        # Si el usuario completó el escenario correctamente
        if user_interaction_count[user_id] >= 3:
            return "¡Buen trabajo! Has completado este escenario de phishing. ¿Te gustaría intentar otro?"

        return bot_response

    except Exception as e:
        return f"Error inesperado: {str(e)}"

# Función principal para la ejecución del chatbot
def main():
    """Ejecuta el chatbot en la terminal."""
    print("\n💻 Bienvenido al entrenamiento de detección de phishing.")
    
    user_id = input("Por favor, ingresa tu ID de usuario: ")
    
    scenario = get_new_scenario()
    
    if not scenario:
        print("⚠️ No se encontraron escenarios disponibles en la base de datos.")
        return

    print(f"\n📌 **Escenario:** {scenario['text']}\n")

    while True:
        user_message = input("Responde al escenario de phishing (o 'salir' para terminar): ")
        
        if user_message.lower() == "salir":
            print("\n🔚 ¡Gracias por participar en el entrenamiento! Nos vemos pronto.")
            break

        if user_message.lower() == "sí":
            scenario = get_new_scenario()
            if scenario:
                print(f"\n📌 **Nuevo escenario:** {scenario['text']}\n")
            else:
                print("⚠️ No hay más escenarios disponibles.")
            continue

        bot_response = get_chatbot_response(user_id, scenario, user_message)
        print(f"\n🤖 **Chatbot:** {bot_response}\n")

if __name__ == "__main__":
    main()
