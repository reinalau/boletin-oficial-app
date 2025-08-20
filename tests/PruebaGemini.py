# To run this code you need to install the following dependencies:
# pip install google-genai

import base64
import os
from google import genai
from google.genai import types


def generate():
    client = genai.Client(
        # Reemplazar con apikey
        api_key='xxxxxxx',
    )

    model = "gemini-2.5-flash"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="""Analiza los puntos mas importantes de el contenido de la Primera Sección del Boletín Oficial de la República Argentina - Sección 1 - Legislación y Avisos Oficiales para la Edición de fecha 2025-08-11
INSTRUCCIONES BUSQUEDA:
Si la fecha 2025-08-11 coincide con la fecha actual en la que se ejecuta este prompt, entonces: Accede a la información del Boletín Oficial de la Republica Argentina para la primera sección "Legislación y Avisos Oficiales" en: https://s3.arsat.com.ar/cdn-bo-001/pdf-del-dia/primera.pdf
Ignorar conflictos de fechas internas en el documento de la url ya que aqui se recopilan erratas y nuevas normativas publicadas con la nueva fecha 2025-08-11.
Si la fecha 2025-08-11 NO coincide con la fecha actual en la que se ejecuta este prompt, entonces: buscar,analizar y resumir la información del Boletín Oficial de La República Argentina de la Primera Sección buscando la edición de dicha fecha.
INSTRUCCIONES PARA EL ANÁLISIS REQUERIDO:
Tomar la fuente seleccionada anteriormente para analizar y hacer el resumen ejecutivo de los cambios normativos relevantes como privatizaciones, área previsional, desregulaciones importantes (para la fecha indicada).
Lista detallada de cambios principales: decretos, resoluciones, disposiciones, avisos oficiales, convenciones colectivas de trabajo y si se identifican cambio en leyes.
Impacto estimado de los cambios.
Áreas del derecho afectadas.
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
Responde ÚNICAMENTE con el JSON válido, sin texto adicional.
Asegúrate de que todas las áreas afectadas estén en minúsculas."""),
            ],
        ),
    ]
    tools = [
        types.Tool(url_context=types.UrlContext()),
        types.Tool(googleSearch=types.GoogleSearch(
        )),
    ]
    generate_content_config = types.GenerateContentConfig(
        thinking_config = types.ThinkingConfig(
            thinking_budget=0,
        ),
        media_resolution="MEDIA_RESOLUTION_UNSPECIFIED",
        tools=tools,
        temperature=0,
    )

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        print(chunk.text, end="")

if __name__ == "__main__":
    generate()
