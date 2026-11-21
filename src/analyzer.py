import os
import json
from dotenv import load_dotenv
from groq import Groq

# 1. Cargamos las variables del archivo .env (tu clave secreta)
load_dotenv()

# 2. Creamos el cliente de conexión con Groq
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Modelo gratuito, rápido y muy bueno en español
MODELO = "openai/gpt-oss-120b"


def analizar_resena(comentario: str, puntuacion: int) -> dict:
    """
    Envía una reseña a Groq y devuelve un diccionario con:
    sentimiento, categoria, urgencia, resumen y respuesta_sugerida.
    """
    prompt_sistema = """
    Eres un analista experto en experiencia de cliente (Customer Operations).
    Analiza la reseña del cliente y responde ÚNICAMENTE con un objeto JSON válido
    que tenga exactamente estas 5 claves:
    - "sentimiento": solo puede ser "Positivo", "Neutro" o "Negativo".
    - "categoria": elige UNA de estas opciones -> "Envío", "Producto", "Atención al cliente", "Precio", "Web/Pagos", "Otro".
    - "urgencia": solo puede ser "Alta" (queja grave, cobro duplicado, reclamación), "Media" (problema menor) o "Baja" (elogio o comentario leve).
    - "resumen": resume el motivo principal en máximo 10 palabras.
    - "respuesta_sugerida": redacta una respuesta empática, profesional y breve en español lista para enviar al cliente.
    """

    prompt_usuario = f"Puntuación del cliente: {puntuacion}/5\nComentario: {comentario}"

    try:
        respuesta = client.chat.completions.create(
            model=MODELO,
            messages=[
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": prompt_usuario},
            ],
            temperature=0.2,  # Baja temperatura = respuestas más consistentes y menos "creativas"
            response_format={"type": "json_object"},  # Obliga a la IA a devolver JSON limpio
        )

        texto_json = respuesta.choices[0].message.content
        return json.loads(texto_json)

    except Exception as e:
        # Si algo falla (sin internet, límite de API, etc.), la app no se rompe
        return {
            "sentimiento": "Error",
            "categoria": "Error",
            "urgencia": "Baja",
            "resumen": f"Error al analizar: {str(e)}",
            "respuesta_sugerida": "",
        }


# Bloque de prueba: solo se ejecuta si lanzamos este archivo directamente
if __name__ == "__main__":
    comentario_prueba = "Me cobraron dos veces el mismo pedido y llevo cuatro días esperando el reembolso sin respuesta."
    print("Enviando reseña de prueba a Groq...\n")
    resultado = analizar_resena(comentario_prueba, puntuacion=1)
    print(json.dumps(resultado, indent=2, ensure_ascii=False))