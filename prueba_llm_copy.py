import requests
import os
import json
import logging
from datetime import datetime
import time
from itertools import cycle


def crear_sesion_fresca():
    """Crea una nueva sesión con cookies frescas"""
    session = requests.Session()
    
    # Visitar página principal para establecer sesión
    session.get('https://www.boletinoficial.gob.ar/seccion/primera')
    time.sleep(1)
    return session


session = crear_sesion_fresca()

url1= 'https://www.boletinoficial.gob.ar/edicion/actualizar/13-08-2025'


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
    import base64
    pdf_bytes = base64.b64decode(pdf_base64)
    
    with open('seccion_primera_20250813.pdf', 'wb') as f:
        f.write(pdf_bytes)
else:
    print(f"Error: {response.status_code}")


