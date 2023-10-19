from bs4 import BeautifulSoup
import requests
import json
import datetime
from urllib.request import urlopen
from urllib.error import HTTPError
from urllib.parse import urlparse, parse_qs
import re


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
date_today = datetime.datetime.now().strftime("%d-%m-%Y")

#recorrer el contendor de la primera pagina que aparece en el buscador
for container in containers:
    heading = container.find('h3', class_='LC20lb MBeuO DKV0Md').text
    link = container.find('a')['href']
    article_summary = div_summary.find('span').text
    icon = container.find('img', class_ = 'XNo5Ab')['src']
    
    #imprimir datos basicos, antes de la pagina web, en el buscador de web de google
    if heading and link:
        print("")
        print(f'Heading: {heading}')
        print(f'Link: {link}')
        print(f'Summary: {article_summary}')
        #print(f'icon image: {icon}')
        print(f'start date: {date_today}')
        break  # Detenerse después de encontrar el primer resultado válido

if not heading or not link:
    print('No se encontraron resultados de búsqueda válidos.')

#funcion obtiene los idiomas de la pagina web

try: 
    html = urlopen(link)
except HTTPError as e:
     None
try:

    bsObj = BeautifulSoup(html, "html.parser")
    email_links = bsObj.find_all('a', href=re.compile(r'^mailto:([A-Za-z0-9\._+]+@[A-Za-z-z0-9]+\.[A-Za-z])'))
    #tlf_links = bsObj.find_all('a', href=re.compile(r'\+\d{1,4} \d{3} \d{3} \d{3}'))
except AttributeError as e:
    None
#Función para encontrar números de teléfono en el contenido de la página

for link in email_links:
    email = link['href'].replace('mailto:', '')
    print(f'Dirección de correo electrónico: {email}')
# for link in tlf_links:
#     # Extrae el número de teléfono del enlace
#     tlf = re.search(r'\+\d{1,4} \d{3} \d{3} \d{3}', link['href'])
#     if tlf:
#         print(f'Número de teléfono: {tlf.group()}')
#     else:
#         print("nada")

def find_phone_numbers(text):
    phone_numbers = re.findall(r'\+\d{1,4}\d{3}\d{3}\d{3}', text)
    return phone_numbers

try:
    html = requests.get(link, headers=headers).text
except requests.exceptions.RequestException as e:
    print('Error al obtener la página:', e)

# Busca números de teléfono en el contenido de la página web
phone_numbers = find_phone_numbers(html)

# Imprime los números de teléfono encontrados
if phone_numbers:
    for phone in phone_numbers:
        print(f'Número de teléfono encontrado: {phone}')
else:
    print('No se encontraron números de teléfono en la página web.')



def get_tlf(url):
    try:
        html = urlopen(url)
    except (HTTPError, URLError) as e:
        print(f'Error en get_tlf: {e}')
        return None
    try:
        bsObject = BeautifulSoup(html, 'html.parser')
        # Extrae el texto visible de la página web
        visible_text = bsObject.get_text()
        # Utiliza una expresión regular para encontrar números de teléfono con o sin texto precedente
        phone_numbers_with_text = re.findall(r'(\S*?):? (\+\d{1,4} \d{3} \d{3} \d{3})', visible_text) 

        # Busca números de teléfono dentro de enlaces (<a>) con atributo href que comienza con 'tel:'
        phone_links = bsObject.find_all('a', href=re.compile(r'^tel:(\+\d{1,4}[\s\d]*)'))
        phone_numbers_in_links = [re.search(r'^tel:(\+\d{1,4}[\s\d]*)', link['href']).group(1).replace(' ', '') for link in phone_links]

        # Agrega números de teléfono de enlaces a la lista si no están en la lista original
        for phone_number in phone_numbers_in_links:
            if phone_number not in [phone for (_, phone) in phone_numbers_with_text]:
                phone_numbers_with_text.append(('', phone_number))

        # Busca números de teléfono con diferentes formatos en el contenido HTML
        # Busca números de teléfono con el formato "(+34) 946 41 51 19" en el contenido HTML
        phone_numbers_in_html = re.findall(r'\(\+\d{1,4}\)\s*\d{3}\s*\d{2}\s*\d{2}\s*\d{2}', visible_text)
        # Agrega la nueva expresión regular para buscar números con el formato "+(34) 984 086 203"
        phone_numbers_in_html += re.findall(r'\+\(\d{2,3}\)\s*\d{3}\s*\d{3}\s*\d{3}', visible_text)
        # Agrega la nueva expresión regular para buscar números con el formato "+33 (0)7 80 98 92 23"
        phone_numbers_in_html += re.findall(r'\+\d{2,3}\s*\(\d\)\s*\d{1,2}[\s\d]*', visible_text)
        # Agrega la nueva expresión regular para buscar números con el formato "657 123 123
        phone_numbers_in_html += re.findall(r'\+\s*\d{3}\s*\d{3}\s*\d{3}', visible_text)
        # Agrega la nueva expresión regular para buscar números con el formato "(+34) 946.855.710"
        phone_numbers_in_html += re.findall(r'\(\+\d{2,3}\)\s*\d{3}.\d{3}.\d{3}', visible_text)
        # Agrega la nueva expresión regular para buscar números con el formato +(34) 636957494
        phone_numbers_in_html += re.findall(r'\+\(\d{2,3}\)\s*\d{9}', visible_text)
        # Agrega la nueva expresión regular para buscar números con el formato href:tel943042213
        phone_numbers_in_html += re.findall(r'tel:(\d{9})', str(bsObject))
        # Agrega la nueva expresión regular para buscar números con el formato +34 943 84 84 51
        phone_numbers_in_html += re.findall(r'\+\d{2,3}\s\d{3}(?:\s\d{2}){2,3}', visible_text)
        # Elimina los caracteres no deseados y almacena los números de teléfono en el formato deseado
        formatted_phone_numbers = [re.sub(r'[^\d+]', '', phone_number) for phone_number in phone_numbers_in_html]

        for phone_number in formatted_phone_numbers:
            if phone_number not in [phone for (_, phone) in phone_numbers_with_text]:
                phone_numbers_with_text.append(('', phone_number))
        #Encortra el número de teléfono con el formato deseado, dentro de etiqueta <p> / <p>
        p_elements = bsObject.find_all('p')
        for p in p_elements:
            #+34 648 764 342
            phone_number = re.search(r'\+\d{2,3}\s\d{3}(?:\s\d{2}){2,3}', p.text)
            phone_number = re.search(r'\s\d{3}(?:\s\d{2}){2,3}', p.text)
            if phone_number:
                phone_numbers_with_text.append(('', phone_number.group()))
        #Encontrar el número de teléfono con el formato deseado, dentro de etiqueta <span> / <span>
        span_elements = bsObject.find_all('span')
        for span in span_elements:
            #+34 648 764 342
            phone_number = re.search(r'\+\d{2,3}\s\d{3}\s\d{3}\s\d{3}', span.text)
            #642 20 21 21
            phone_number = re.search(r'\b\d{3} \d{2} \d{2} \d{2}\b', span.text)
            
            if phone_number:
                phone_numbers_with_text.append(('', phone_number.group()))
         
            if phone_number:
                phone_numbers_with_text.append(('', phone_number.group()))
    except AttributeError as e:
        return None

    return phone_numbers_with_text
