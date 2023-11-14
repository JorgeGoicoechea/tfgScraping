from bs4 import BeautifulSoup as bs
import requests 
import json
import datetime
from urllib.request import urlopen, Request
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
soup = bs(html, 'lxml')

# Encuentra todos los contenedores de resultados de búsqueda
containers = soup.findAll('div', class_='yuRUbf')
div_summary = soup.find('div', class_='VwiC3b yXK7lf lyLwlc yDYNvb W8l4ac lEBKkf')
if div_summary is None:
     div_summary = soup.find('div', class_='VwiC3b yXK7lf lyLwlc yDYNvb W8l4ac')

# Imprimir el resultado
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
    prueba =div_summary.find('span') 
    article_summary = None
    if div_summary is not None:
        if div_summary.find('span') is not None:
             article_summary = div_summary.find('span').text
             #cuando lo que detecta es la fecha antes del div, la quitamos para obtener el texto restante
             if len(article_summary) < 20:
                article_summary = div_summary.get_text().split('—', 1)[-1].strip()
        else:
             article_summary = div_summary.text
             #cuando lo que detecta es la fecha antes del div, la quitamos para obtener el texto restante
             if len(article_summary) < 20:
                    article_summary = div_summary.get_text().split('—', 1)[-1].strip()

    icon = None
    img = container.find('img', class_='XNo5Ab')
    if img:
          icon = img['src']
    
    #imprimir datos basicos, antes de la pagina web, en el buscador de web de google
    if heading and link:
        print("")
        #print(f'Heading: {heading}')
        print(f'Link: {link}')
        print(f'Summary: {article_summary}')
        #print(f'icon image: {icon}')
        #print(f'start date: {date_today}')
        break  # Detenerse después de encontrar el primer resultado válido

if not heading or not link:
    print('No se encontraron resultados de búsqueda válidos.')
def get_social_media(url):
    try:
        req = Request(url, headers=headers)
        html = urlopen(req)
    except (HTTPError, URLError) as e:
        print(f'Error en get_social_media: {e}')
        return None

    bsObject = bs(html, 'html.parser')

    # Encuentra la etiqueta <a> con enlaces de LinkedIn (insensible a mayúsculas y minúsculas)
    linkedin_tag = bsObject.find('a', href=re.compile(r'linkedin', re.I))
    linkedin_url = linkedin_tag['href'] if linkedin_tag else None
    if linkedin_tag:
        linkedin_url = linkedin_tag['href']
    else:
        # Si no se encuentra dentro de <a>, verifica el atributo href del elemento <a>
        all_links = bsObject.find_all('a')
        for link in all_links:
            href = link.get('href')
            if href and 'linkedin.com' in href:
                linkedin_url = href
                break
        else:
            linkedin_url = None
    #crear url ala pagina de linkedin con el nombre de la empresa, cuando hay espacion entre palabras poner -
    if linkedin_url == None:
        linkedin_url = 'https://www.linkedin.com/company/' + empresa.replace(' ', '-')
        #respuesta 999 todavia no tengo permisos para entrar a la pagina de linkedin
        response = requests.get(linkedin_url)
        print("respuesta" , response.status_code)
        if response.status_code == 404:
            linkedin_url = None

    # Encuentra la etiqueta <a> con enlaces de Twitter (insensible a mayúsculas y minúsculas)
    twitter_tag = bsObject.find('a', href=re.compile(r'twitter', re.I))
    # twitter_url = twitter_tag['href'] if twitter_tag 
    if twitter_tag :
        twitter_url = twitter_tag['href']
    else:
        # Si no se encuentra dentro de <a>, verifica el atributo href del elemento <a>
        all_links = bsObject.find_all('a')
        for link in all_links:
            href = link.get('href')
            if href and 'twitter.com' in href:
                twitter_url = href
                break
        else:
            twitter_url = None
    return linkedin_url, twitter_url

social_media_urls = get_social_media(link)

if social_media_urls:
    linkedin_url, twitter_url = social_media_urls
    print(f'LinkedIn URL: {linkedin_url}')
    print(f'Twitter URL: {twitter_url}')
else:
    print('No se encontraron enlaces de LinkedIn ni de Twitter.')
