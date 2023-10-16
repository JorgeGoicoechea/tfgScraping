from bs4 import BeautifulSoup
import requests
import json
import datetime
from urllib.request import urlopen
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse, parse_qs
from langdetect import detect

import re


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
    div_summary = div_summary.find('span') 
    if div_summary:
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
    

def get_contact_link(url):
    try:
        html = urlopen(url)
    except (HTTPError, URLError) as e:
        print(f'Error en get_contact_link: {e}')
        return None
    try:
        bsObject = BeautifulSoup(html, 'html.parser')
        # Encuentra el primer enlace que contiene la palabra "contacto" en su URL
        contact_link = bsObject.find('a', href=re.compile(r'contact', re.I))

        if contact_link:
            return contact_link['href']

        return None
    except AttributeError as e:
        return None

# Reemplaza 'URL_DE_LA_PAGINA' con la URL de la página de la que deseas obtener el enlace de contacto
contact_url = get_contact_link(link)

if contact_url:
    print(contact_url)
else:
    print('No se encontró un enlace de contacto en la página web.')