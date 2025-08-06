# To run this code you need to install the following dependencies:
# pip install google-genai

import base64
import os
from google import genai
from google.genai import types


def generate():
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

    model = "gemini-2.5-flash"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="""
                Analiza el contenido del Boletín Oficial de la República Argentina para la fecha actual.

INSTRUCCIONES:

Accede a la información del Boletín Oficial desde: https://www.boletinoficial.gob.ar/

Busca específicamente la sección 1 "Legislación y Avisos Oficiales" para la fecha actual

Identifica y analiza todos los cambios normativos publicados en esa fecha

Si no encuentras contenido para esa fecha exacta, busca la fecha hábil más cercana

Si es fin de semana o feriado, busca el día hábil anterior

ANÁLISIS REQUERIDO:

Resumen ejecutivo de los cambios normativos

Lista detallada de cambios principales (decretos, resoluciones, leyes)

Impacto estimado de los cambios

Áreas del derecho afectadas

FORMATO DE RESPUESTA (JSON válido):
{{
"resumen": "Resumen ejecutivo de los cambios normativos encontrados para la fecha actual",
"cambios_principales": [
{{
"tipo": "decreto|resolución|ley|disposición",
"numero": "número del instrumento legal",
"titulo": "título o tema principal",
"descripcion": "descripción detallada del cambio",
"impacto": "alto|medio|bajo",
"justificacion_impacto": "explicación del nivel de impacto"
}}
],
"impacto_estimado": "Análisis general del impacto de todos los cambios",
"areas_afectadas": ["tributario", "laboral", "comercial", "civil", "penal", "administrativo", "otros"]
}}

IMPORTANTE:

Responde ÚNICAMENTE con el JSON válido, sin texto adicional

Si no encuentras contenido para la fecha, indica en el resumen que no hay publicaciones

Asegúrate de que todas las áreas afectadas estén en minúsculas

Fecha a analizar: {date}

URL de referencia: https://www.boletinoficial.gob.ar/ """),
            ],
        ),
    ]
    tools = [
        types.Tool(googleSearch=types.GoogleSearch(
        )),
    ]
    generate_content_config = types.GenerateContentConfig(
        thinking_config = types.ThinkingConfig(
            thinking_budget=-1,
        ),
        tools=tools,
    )

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        print(chunk.text, end="")

if __name__ == "__main__":
    generate()
