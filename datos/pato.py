from bs4 import BeautifulSoup
import requests
import json
import datetime
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse, parse_qs
from langdetect import detect

import re

#arreglar problema cretificate verify failed
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
#arreglar problema unsafe_legacy_renegotiation_disabled.
#hemos creado archivo openssl.cnf
#llamada terminal con el scraper OPENSSL_CONF=/home/jorge/tfg/openssl.cnf python pruebastack.py



headers = {

    'authority': 'www.google.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'cache-control': 'max-age=0',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.150Safari/537.36',
    # Add more headers as needed
}


empresa = input("empresa: ")
html = requests.get('https://www.google.com/search?q={empresa}'.format(empresa=empresa),
                    headers=headers).text

soup = BeautifulSoup(html, 'lxml')

# Encuentra todos los contenedores de resultados de búsqueda
containers = soup.findAll('div', class_='yuRUbf')
div_summary = soup.find('div', class_='VwiC3b yXK7lf lyLwlc yDYNvb W8l4ac lEBKkf')
if div_summary is None:
     div_summary = soup.find('div', class_='VwiC3b yXK7lf lyLwlc yDYNvb W8l4ac')
date_today = datetime.datetime.now().strftime("%d-%m-%Y")

#recorrer el contendor de la primera pagina que aparece en el buscador
for container in containers:
    heading = None
    h3 = container.find('h3', class_='LC20lb MBeuO DKV0Md')
    if h3:
          heading = h3.text
          
    link = None  
    a = container.find('a')
    if a:
          link = a['href']

    article_summary = None
    if div_summary is not None:
        if div_summary.find('span') is not None:
             article_summary = div_summary.find('span').text
        else:
             article_summary = div_summary.text

    icon = None
    img = container.find('img', class_='XNo5Ab')
    if img:
          icon = img['src']
    
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

#funcion para obtener el link de la pagina de los contactos de la empresa haciendo un crawling para obtener datos de contacto
def get_contact_link(url):
    try:
        #arreglar error 406
        req = Request(url, headers=headers)
        html = urlopen(req)
    except (HTTPError, URLError) as e:
        print(f'Error en get_contact_link: {e}')
        return None
    try:
        bsObject = BeautifulSoup(html, 'html.parser')
        # Encuentra el primer enlace que contiene la palabra "contacto" en su URL
        contact_link = bsObject.find('a', href=re.compile(r'contact'))
        href_value = None
        # Verifica si se encontró un enlace
        if contact_link:
            href_value = contact_link.get('href')  # Obtiene el valor del atributo href
            print(f'Contact link: {href_value}')

        # Encuentra el elemento <a>, llamada recorrer todo 
        else:
            all_links = bsObject.find_all('a')
            for link in all_links:
                href = link.get('href')
                if href and '/contact/' in href:
                    href_value = contact_link.get('href')  # Obtiene el valor del atributo href
                    print(f'Contact link: {href_value}')
                    break  # Detenerse después de encontrar el primer enlace de contacto
        return href_value
    except Exception as e:
        print(f'Error al buscar el enlace de contacto: {e}')
        return None

def remove_duplicates(numbers):
    unique_numbers = []
    for num in numbers:
        postfix = re.sub(r'[^\d]', '', num)
        if postfix not in [re.sub(r'[^\d]', '', u) for u in unique_numbers]:
            unique_numbers.append(num)
    return unique_numbers    
#funcion obtiene los tlf de la pagina web

def get_tlf(url):
    try:
        req = Request(url, headers=headers)
        html = urlopen(req)
    except (HTTPError, URLError) as e:
        print(f'Error en get_tlf: {e}')
        return None
    try:
        phone_numbers_with_text = []
        bsObject = BeautifulSoup(html, 'html.parser')
        # Extrae el texto visible de la página web
        visible_text = bsObject.get_text()
        # Utiliza una expresión regular para encontrar números de teléfono,+34 666 666 666
        phone_numbers_with_text = re.findall(r'\+\d{2,3}\s\d{3}\s\d{3}\s\d{3}', visible_text)
        # Agrega la nueva expresión regular para buscar números con el formato +34 943 84 84 51
        phone_numbers_with_text += re.findall(r'\+\d{1,4}\s\d{3}(?:\s\d{2}){2,3}', visible_text)
        # Expresión regular para encontrar números de teléfono en el formato +34 946522767
        phone_numbers_with_text += re.findall(r'\+\d{2,3} \d{9}', visible_text)
        # Busca números de teléfono con el formato "(+34) 946 41 51 19" 
        phone_numbers_with_text += re.findall(r'\(\+\d{1,4}\)\s*\d{3}\s*\d{2}\s*\d{2}\s*\d{2}', visible_text)
        # Busca números de teléfono con el formato "(+34) 946 415 119" o (+34) 944.991.444
        phone_numbers_with_text += re.findall(r'\(\+\d{2}\)\s*\d{3}(?:[\s\.]\d{3}){2}', visible_text)
        # Busca números de teléfono con el formato (+34) 94 464 65 11 
        phone_numbers_with_text += re.findall(r'\(\+\d{2,4}\)\s*\d{2}\s*\d{3}\s*\d{2}\s*\d{2}', visible_text)
        # Agrega la nueva expresión regular para buscar números con el formato "+33 (0)7 80 98 92 23"
        # phone_numbers_with_text += re.findall(r'\+\d{2,3}\s*\(\d\)\s*\d{1,2}[\s\d]*', visible_text)
        phone_numbers_with_text += re.findall(r'\+\d{2,3}\s*\(\d\)\s*(?:\d\s*){8,}', visible_text)
        # Agrega la nueva expresión regular para buscar números con el formato "(+34) 946.855.710"
        phone_numbers_with_text += re.findall(r'\(\+\d{2,3}\)\s*\d{3}.\d{3}.\d{3}', visible_text)
        #Para la expresión regular del formato "+34 91 663 28 50"
        phone_numbers_with_text += re.findall(r'\+\d{2,2}\s\d{2}\s\d{3}\s\d{2}\s\d{2}', visible_text)
        #La expresión regular para el formato "+972-3-509-4017
        phone_numbers_with_text += re.findall(r'\+\d{2,3}-\d-\d{3}-\d{4}', visible_text)
        #La expresión regular para el formato "+34 911-881-344" 
        phone_numbers_with_text += re.findall(r'\+\d{1,4}\s\d{3}-\d{3}-\d{3}', visible_text)
         #La expresión regular para el formato 1 (877) 889-9009 o 1 866 249-0976
        phone_numbers_with_text += re.findall(r'1\s*(?:\(\d{3}\)|\d{3})\s*\d{3}\-(?:\s*\d{4})', visible_text)
        #La expresión regular para el formato + 34 94 513 1372
        phone_numbers_with_text += re.findall(r'\+\s*\d{2}\s*\d{2}\s*\d{3}\s*\d{4}', visible_text)
        #La expresión regular para el formato +1 724 933 7700
        phone_numbers_with_text += re.findall(r'\+\d{1,4}\s*\d{3}\s*\d{3}\s*\d{4}', visible_text)
        #La expresión regular para el formato 34 91 806 0099
        phone_numbers_with_text += re.findall(r'\d{2,4}\s*\d{2,3}\s*\d{3}\s*\d{4}', visible_text)
        #la ultima de todas porque si no se duplican los números de teléfono
        if not phone_numbers_with_text:
            # Agrega la nueva expresión regular para buscar números con el formato "657 123 123"
            phone_numbers_with_text += re.findall(r'\d{3} \d{3} \d{3}', visible_text)
            # Agrega la nueva expresión regular para buscar números con el formato "657 12 31 23"
            phone_numbers_with_text += re.findall(r'\d{3} \d{2} \d{2} \d{2}', visible_text)
            #La expresión regular para el formato 94 495 73 11
            phone_numbers_with_text += re.findall(r'\d{2}\s\d{3}\s\d{2}\s\d{2}', visible_text)
            #La expresión regular para el formato 944.132.352
            phone_numbers_with_text += re.findall(r' \d{2,3}\.\d{3}\.\d{3}', visible_text)
        # Busca números de teléfono dentro de enlaces (<a>) con atributo href que comienza con 'tel:'
        # Expresión regular para números de teléfono con al menos 9 dígitos
        phone_links = bsObject.find_all('a', href=re.compile(r'^tel:(\+\d{9,}[\s\d]*)'))
        phone_numbers_in_links = [re.search(r'^tel:(\+\d{9,}[\s\d]*)', link['href']).group(1).replace(' ', '') for link in phone_links]
        #FALTA CREAR CHECKEO 34 +34 phone_numbers_with_text: ['+34 955 27 56 49', '+34 955 27 56 49', '34 955 27 56', '34 955 27 56'] PARA
        #  QUE LOS ELIMINE Y YA SE SOLUCIONE TODO
        # Formatea los números de teléfono y quita los espacios solo si son cadenas válidas
        formatted_phone_numbers = [re.sub(r'[^\d+]', '', phone_number) if isinstance(phone_number, str) else '' for phone_number in phone_numbers_with_text]
        # Lista para almacenar los números de teléfono únicos
        unique_formatted_phone_numbers = []

        # Agrega los números de teléfono únicos a la lista
        for phone in formatted_phone_numbers:
            if all(phone != unique_phone for unique_phone in unique_formatted_phone_numbers) and len(unique_formatted_phone_numbers) < 4:
                unique_formatted_phone_numbers.append(phone)

        # Agrega los números de teléfono únicos de phone_numbers_in_links
        for phone in phone_numbers_in_links:
            if all(phone != unique_phone for unique_phone in unique_formatted_phone_numbers) and len(unique_formatted_phone_numbers) < 4:
                unique_formatted_phone_numbers.append(phone)
        
        unique_formatted_phone_numbers = remove_duplicates(unique_formatted_phone_numbers)
        return unique_formatted_phone_numbers
    except AttributeError as e:
        return None


#Obtiene el link del contacto de la pagina web por si no esta toda esa informacion en la pagina de inicio
try:
    contact_link = get_contact_link(link)

    # Llama a la función y obtén la lista de números de teléfono y su texto precedente del inicio o de la página de contacto

    phone_number = get_tlf(link)
    # Imprime los números de teléfono y su texto precedente
    if phone_number:
        for phone in phone_number:
            print(f'Número de teléfono: {phone}')
    if not phone_number:
        if contact_link is None:
            print('No se encontraron números de teléfono en la página web.')
        else:
             #por si el url no es completo, se agrega el dominio a la url para obtener el correo de la pagina de contacto
            if not contact_link.startswith('http'):
                if not contact_link.startswith('/'):
                    base_url = urlparse(link)
                    complete_contact_link = f"{base_url.scheme}://{base_url.netloc}/{contact_link}"
                    phone_number = get_tlf(complete_contact_link)
                else:
                    base_url = urlparse(link)
                    complete_contact_link = f"{base_url.scheme}://{base_url.netloc}{contact_link}"
                    phone_number = get_tlf(complete_contact_link)
            else:
                phone_number = get_tlf(contact_link)
            if not phone_number:
                print('No se encontraron números de teléfono en la página web.')
            else:
                for phone in phone_number:
                    print(f'Número de teléfono: {phone}')


except (HTTPError) as e:
    print(f'problema pagina de contacto: {e}')


    