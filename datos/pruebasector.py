from bs4 import BeautifulSoup
import requests
import json
import datetime
from urllib.request import urlopen,Request
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse, parse_qs
import re
from keybert import KeyBERT
import glob
import string
import nltk
nltk.download('punkt')
nltk.download('stopwords')
from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize
from sklearn.model_selection import train_test_split
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

headers = {
            'User-agent':
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.150 Safari/537.36"
        }
def obtener_texto_web(url):

    # Intenta obtener el texto de la web con request
    try:
        req = Request(url, headers=headers)
        html = urlopen(req)
    except (HTTPError, URLError) as e:

        # Intenta obtener el texto de la web con Selenium como alternativa
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            driver = webdriver.Chrome(options=chrome_options)  # Puedes usar otro navegador y configurar el controlador correspondiente
            driver.get(url)
            html = driver.page_source
        except Exception as e:
            return None
        finally:
            driver.quit()

    try:
        # Parsea el contenido HTML de la página
        soup = BeautifulSoup(html, 'html.parser')

        # Encuentra y concatena todo el texto visible en la página
        texto_visible = ''
        for elemento in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'span', 'a']):
            texto_visible += elemento.get_text() + ' '

        # Elimina caracteres especiales y espacios en blanco adicionales
        texto_visible = ' '.join(texto_visible.split())

        texto_visible = texto_visible.lower()

        return texto_visible
    except Exception as e:

        return f"Error inesperado: {str(e)}"

def eliminar_texto_web(texto):
       # Palabras a eliminar
        palabras_a_eliminar = set(nltk.corpus.stopwords.words('spanish'))
        palabras_personalizadas = {'euskadi','vasca','2020','2021','2022','2023','rellena','ninguno','formulario','linkedin', 'twitter', 'youtube', 'eng', 'esp', 'eu', 'cada', 'día', 'oportunidades', 'negocio', 'personas', 'sitio', 'resultado', 'empresa', 'página', 'minimizar', 'cliente', 'valor', 'trabajo', 'basada', 'nueva', 'uso', 'situaciones', 'complejas', 'patrones', 'tendencias', 'recomendaciones', 'acciones', 'alto', 'valor', 'añadido', 'área', 'ventajas',  'acción', 'manera', 'representación', 'pros', 'interactiva', 'acceso', 'limitada', 'difícil', 'cantidad',  'percepción', 'crítica',  'scada', 'hmi', 'personalizable',  'inmersivo', 'operación', 'incidencias', 'conocimientos', 'superpoder', 'inmersivos','pasar', 'comunicación', 'información', 'fácil', 'clima',  'electromagnético', 'socio',  'puerta', 'futuro', 'última', 'humanidad',  'capacidad', 'ayudarte', 'poner', 'cámara', 'limpia', 'terreno', 'acuerdo', 'alianza', 'liderar',  'pequeños',  'oportunidades', 'desconectar', 'usuarios', 'abonado', 'propósito',  'preferencias', 'finalidad', 'almacenar', 'solicitadas', 'anónimos', 'requerimiento', 'proveedor',  'registros', 'tercero',  'utilizar', 'identificarte', 'marketing', 'crear', 'perfiles', 'enviar', 'publicidad', 'rastrear','usar', 'legítima', 'cumplimiento', 'voluntario'}
        palabras_a_eliminar = palabras_a_eliminar.union(palabras_personalizadas)
        palabras_a_eliminar = list(palabras_a_eliminar)

        # Construye una expresión regular para buscar las palabras a eliminar
        pattern = r'\b(?:' + '|'.join(re.escape(word) for word in palabras_a_eliminar) + r')\b'

        # Usa la expresión regular para eliminar las palabras
        texto_visible = re.sub(pattern, '', texto)

        # Usa una expresión regular para eliminar palabras entre llaves
        texto_visible = re.sub(r'\{[^}]+\}', '', texto_visible)

        return texto_visible


# Define una función que obtenga el texto de la web y lo almacene en el archivo Excel
def obtener_y_guardar_texto(empresa, excel_file):
    try:

        html = requests.get('https://www.google.com/search?q={empresa}'.format(empresa=empresa),
                            headers=headers).text

        soup = BeautifulSoup(html, 'lxml')

        # Encuentra todos los contenedores de resultados de búsqueda
        containers = soup.findAll('div', class_='yuRUbf')

        #recorrer el contendor de la primera pagina que aparece en el buscador para el link
        for container in containers:
            link = container.find('a')['href']
            break
        if not  link:
            print('No se encontraron resultados de búsqueda válidos.')
        print(link)
        texto_visible = obtener_texto_web(link)

        if texto_visible:
            texto_modificado = eliminar_texto_web(texto_visible)
            # Abre el archivo Excel
            df = pd.read_excel(excel_file)

            # Busca la fila con el nombre de la empresa y agrega el texto en la columna correspondiente
            index = df[df['Empresa'] == empresa].index

            if len(index) > 0:
                df.at[index[0], 'Texto'] = texto_modificado

                # Guarda los cambios en el archivo Excel
                df.to_excel(excel_file, index=False)
                
            else:
                print(f"No se encontró la empresa: {empresa}")
        else:
            print(f"No se pudo obtener el texto de la página web para la empresa: {empresa}")
    
    except Exception as e:
        print(f"Error inesperado: {str(e)}")

# Carga el archivo Excel que contiene la lista de empresas y crea una lista de empresas
excel_file = '/home/jorge/tfg/datos/clasificacionsector.xlsx'
df = pd.read_excel(excel_file)
empresas = df['Empresa'].tolist()

# Procesa cada empresa y guarda el texto en el archivo Excel
for empresa in empresas:
    texto = obtener_y_guardar_texto(empresa, excel_file)
    