import requests
import os
import json
import logging
import base64
import time
from datetime import datetime
from typing import Dict, Any, Optional
from google import genai
from google.genai import types

def crear_sesion_fresca():
    """Crea una nueva sesión con cookies frescas"""
    session = requests.Session()
    
    # Visitar página principal para establecer sesión
    session.get('https://www.boletinoficial.gob.ar/seccion/primera')
    time.sleep(1)
    return session


session = crear_sesion_fresca()

url1= 'https://www.boletinoficial.gob.ar/edicion/actualizar/23-08-2025'

response = session.get(url1)

url2 = "https://www.boletinoficial.gob.ar/pdf/download_section"
headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://www.boletinoficial.gob.ar',
        'Referer': 'https://www.boletinoficial.gob.ar/seccion/primera',
        'X-Requested-With': 'XMLHttpRequest',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
    }
data = {
    'nombreSeccion': 'primera',
}

# Hacer petición POST con la sesión establecida
response = session.post(url2, data=data, headers=headers, timeout=30)

#response = request.post(url, data=data)

if response.status_code == 200:
    # La respuesta es JSON con el PDF en Base64
    json_data = response.json()
    pdf_base64 = json_data['pdfBase64']
    
    # Decodificar y guardar el PDF
   # import base64
   # pdf_bytes = base64.b64decode(pdf_base64)
    
   # with open('seccion_primera_20250812.pdf', 'wb') as f:
   #     f.write(pdf_bytes)
else:
    print(f"Error: {response.status_code}")


prompt_text = f"""
        Actua como un experto en asuntos Legales y Técnicos gubernamentales para analizar los puntos mas importantes de el contenido adjunto de la Primera Sección del Boletín Oficial de la República Argentina: Legislación y Avisos Oficiales para la Edición adjunto de fecha 20250823
        
        INSTRUCCIONES PARA EL ANÁLISIS REQUERIDO:
        - Tomar la fuente adjunta  para analizar y hacer el resumen ejecutivo de los cambios normativos relevantes como privatizaciones, área previsional, desregulaciones importantes (para la fecha indicada).
        - Lista detallada de cambios principales: decretos, resoluciones, disposiciones, avisos oficiales, convenciones colectivas de trabajo y si se identifican cambio en leyes.
        - Impacto estimado de los cambios.
        - Áreas del derecho afectadas.

        FORMATO DE RESPUESTA (JSON válido):
        {{
        "resumen": "Resumen ejecutivo de los cambios normativos encontrados para la fecha",
        "cambios_principales": [
        {{
        "tipo": "decreto|resolución|ley|disposición",
        "numero": "número del instrumento legal",
        "rotulo": "Titulo exacto completo asociado al instrumento legal (Ejemplo: AGENCIA DE RECAUDACIÓN Y CONTROL ADUANERO. DIRECCIÓN REGIONAL SANTA FE. Disposición 44/2025)",
        "titulo": "título del tema principal",
        "descripcion": "Resumen ejecutivo y descripción del cambio",
        "impacto": "alto|medio|bajo",
        "justificacion_impacto": "explicación del nivel de impacto"
        }}
        ],
        "impacto_estimado": "Análisis general del impacto de todos los cambios",
        "areas_afectadas": ["tributario", "laboral", "comercial", "civil", "penal", "administrativo", "otros"]
        }}

        IMPORTANTE:
        Responde ÚNICAMENTE con el JSON válido, sin texto adicional.
        Asegúrate de que todas las áreas afectadas estén en minúsculas.
        Responder en Español.
        """



client = genai.Client(
    #Obtener apikey de google gemini
        api_key="AIzaSyD3aqlgDVOxwmFdjk8pyWpWJ7gnzLko2hI",
    )

model = "gemini-2.5-flash"
contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_bytes(
                    mime_type="application/pdf",
                    data=base64.b64decode(
                        pdf_base64
                    ),
                ),
                types.Part.from_text(text=prompt_text),
            ],
        ),
]
tools = [
        types.Tool(url_context=types.UrlContext()),
        types.Tool(googleSearch=types.GoogleSearch(
        )),
]
generate_content_config = types.GenerateContentConfig(
        temperature=0,
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
