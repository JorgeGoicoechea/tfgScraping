from bs4 import BeautifulSoup
import requests
import json
import datetime
from urllib.request import urlopen
from urllib.error import HTTPError
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
headers = {
    'User-agent':
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.150 Safari/537.36"
}


empresa = input("empresa: ")
html = requests.get('https://www.google.com/search?q={empresa}'.format(empresa=empresa),
                    headers=headers).text

soup = BeautifulSoup(html, 'lxml')

# Encuentra todos los contenedores de resultados de búsqueda
containers = soup.findAll('div', class_='yuRUbf')
div_summary = soup.find('div', class_='VwiC3b yXK7lf lyLwlc yDYNvb W8l4ac lEBKkf')

#recorrer el contendor de la primera pagina que aparece en el buscador
for container in containers:
    
    link = container.find('a')['href']

if not  link:
    print('No se encontraron resultados de búsqueda válidos.')

def obtener_texto_web(url):
    try:
        # Realiza una solicitud GET a la URL
        response = requests.get(url)
        response.raise_for_status()

        # Parsea el contenido HTML de la página
        soup = BeautifulSoup(response.text, 'html.parser')

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
archivos =[]
textos = []
etiquetas = []
directorio = "/home/jorge/tfg/datos/"
txt = f"{directorio}/*.txt"
# Ejemplo de uso
texto = obtener_texto_web(link)
print(texto)
if not texto:
    print("No se pudo obtener el texto de la página web.")
else :
    texto_modificado = eliminar_texto_web(texto)
    oraciones = sent_tokenize(texto_modificado)
    print(texto_modificado)
    frases = []
    for oracion in oraciones:
        palabras = word_tokenize(oracion)
        
        # Divide las palabras en fragmentos de cierta longitud (por ejemplo, 5 palabras)
        longitud_fragmento = 5
        fragmentos = [palabras[i:i+longitud_fragmento] for i in range(0, len(palabras), longitud_fragmento)]
        # Convierte los fragmentos de palabras nuevamente en frases
        frases.extend([' '.join(fragmento) for fragmento in fragmentos])

    # Guarda las frases en el archivo
    nombre_archivo = f"{empresa}.txt"
    with open(nombre_archivo, "w", encoding="utf-8") as file:
        for frase in frases:
            # Limpia la frase eliminando signos de puntuación
            frase_limpia = frase.translate(str.maketrans('', '', string.punctuation))
            if frase_limpia.strip():
                file.write(frase_limpia + '\n')  # Escribe la frase en una nueva línea


        archivos.append(nombre_archivo)
        archivos_txt = glob.glob(txt)
    
#     for etiqueta, f in enumerate(archivos_txt):
#         print(f"{f} Corresponde a la etiqueta {etiqueta}")
#         print("\n")
#         with open(f, "r", encoding="utf-8") as file:
#             for line in file:
#                 if line:
#                     textos.append(line)
#                     etiquetas.append(etiqueta)
#     #print(etiquetas)     
#     #tomar los textos y dividirlos en un conjunto de entrenamiento y prueba. Entonces hay textos que van a servir para entrenar el modelo
#     #y otro para testear los modelos
#     #random state es semilla
#     train_text, test_text, Ytrain, Ytest = train_test_split(textos, etiquetas, test_size=0.1, random_state=42)
    
