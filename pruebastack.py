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

#funcion para obtener el link de la pagina de los contactos de la empresa haciendo un crawling para obtener datos de contacto
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

#funcion obtiene los idiomas de la pagina web
def get_idiomas(url):
    try:
         html = urlopen(url)
    except (HTTPError,URLError) as e:
         print(f'Error en get_idiomas: {e}')
         return None
    try:
         bsObject = BeautifulSoup(html, 'html.parser')
         # Busca todas las etiquetas 'link' con atributo 'hreflang', justo son las de los idiomas de todas las paginas
         hreflang_tags = bsObject.find_all('link', {'rel': 'alternate', 'hreflang': re.compile('.*', re.I)})

    except AttributeError as e:
         return None
    idiomas = []
    if hreflang_tags:
         # Itera sobre las etiquetas y obtén los valores de 'hreflang', esa etiqueta es la que tiene el idioma
         for tag in hreflang_tags:
            hreflang_value = tag['hreflang']
            if len(hreflang_value) <= 4:
                idiomas.append(hreflang_value)
    if not idiomas:
            # Si no se encuentran idiomas en los enlaces, intenta buscar en el atributo 'lang' de la etiqueta 'html'
            html_tag = bsObject.find('html')

            if html_tag:
                html_lang = html_tag.get('lang')

                if html_lang:
                    idiomas.append(html_lang)
                else:
                    # Si no se encuentra un idioma en 'html' ni en los enlaces, detectar idioma de la pagina web
                     detected_lang = detect(bsObject.get_text())
                     idiomas.append(detected_lang)
            else:
                # Si no se encuentra un idioma en 'html' ni en los enlaces, detectar idioma de la pagina web
                     detected_lang = detect(bsObject.get_text())
                     idiomas.append(detected_lang)
    return idiomas

#funcion obtiene los emails de la pagina web
def get_email(url):
    try:
        html = urlopen(url)
    except (HTTPError, URLError) as e:
        print(f'Error en get_email: {e}')
        return None
    try:
        bsObj = BeautifulSoup(html, 'html.parser')
        # Utiliza expresión regular para obtener correos de enlaces 'mailto:'
        email_links = bsObj.find_all('a', href=re.compile(r'^mailto:([A-Za-z0-9\._+]+@[A-Za-z-z0-9]+\.[A-Za-z])'))
        
        # Si se encuentran correos electrónicos en enlaces 'mailto:', devuelve el primero
        if email_links:
            return email_links[0]['href'].replace('mailto:', '')
        
        # Si no se encuentran correos en enlaces 'mailto:', busca correos escritos en el contenido HTML
        email_in_text = re.findall(r'[\w\.-]+@[\w\.-]+', bsObj.get_text())
        
        # Si se encuentran correos en el texto, devuelve el primero
        if email_in_text:
            return email_in_text[0]

        # Si no se encuentra ningún correo, devuelve None
        return None
    except AttributeError as e:
        return None

#funcion obtiene los tlf de la pagina web

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
            phone_number = re.search(r'\+\d{2} \d{2} \d{3} \d{2} \d{2}', p.text)
            #+(34)945 34 34 43
            phone_number = re.search(r'\+\(\d{2,3}\)\s*\d{3}\s*\d{2}\s*\d{2}', p.text)
            #+xx xxx xxx xxx
            #xxx xx xx xx
            #xxx xx xx xx sin +
            phone_number = re.search(r'\+\d{2,3}\s\d{3}(?:\s\d{2}){2,3}|\b\d{3} \d{2} \d{2} \d{2}\b|\b\d{3} \d{2} \d{2} \d{2}\b', p.text)
            if phone_number:
                phone_numbers_with_text.append(('', phone_number.group()))
        #Encontrar el número de teléfono con el formato deseado, dentro de etiqueta <span> / <span>
        span_elements = bsObject.find_all('span')
        for span in span_elements:
            #+34 648 764 342
            phone_number = re.search(r'\+\d{2,3}\s\d{3}\s\d{3}\s\d{3}', span.text)
            #642 20 21 21
            phone_number = re.search(r'\b\d{3} \d{2} \d{2} \d{2}\b', span.text)
            phone_number = re.search(r'\+\d{2,3}\s\d{3}(?:\s\d{2}){2,3}|\b\d{3} \d{2} \d{2} \d{2}\b|\b\d{3} \d{2} \d{2} \d{2}\b', span.text)
            
            if phone_number:
                phone_numbers_with_text.append(('', phone_number.group()))
        
    except AttributeError as e:
        return None

    return phone_numbers_with_text

#Obtiene el link del contacto de la pagina web por si no esta toda esa informacion en la pagina de inicio
try:
    contact_link = get_contact_link(link)
    #llamada para imprimir los idiomas que tenemos en la pagina web
    idiomas = get_idiomas(link)
    if idiomas == None:
        print('No se encontraron idiomas en la página web.')
    else:
        print(f'idiomas: {idiomas}')

    #llamada para imprimir los correos de la pagina web, del inicio o de la pagina de contacto
    email = get_email(link)
    if email == None:
        if contact_link == None:
            print('No se encontró una dirección de correo electrónico en la página web.')
        else :
            #por si el url no es completo, se agrega el dominio a la url para obtener el correo de la pagina de contacto
            if not contact_link.startswith('http'):
                base_url = urlparse(link)
                complete_contact_link = f"{base_url.scheme}://{base_url.netloc}{contact_link}"
                email = get_email(complete_contact_link)
            else:
                #url completa antes, no hace falta agragar nada
                email = get_email(contact_link)
            if email == None:
                print('No se encontró una dirección de correo electrónico en la página web.')
            else:
                print(f'Dirección de correo electrónico: {email}')
    else:
        print(f'Dirección de correo electrónico: {email}')

    # Llama a la función y obtén la lista de números de teléfono y su texto precedente del inicio o de la página de contacto

    phone_numbers_and_text = get_tlf(link)
    # Imprime los números de teléfono y su texto precedente
    if phone_numbers_and_text:
        for item in phone_numbers_and_text:
            text, phone_number = item
            
            print(f' {text} ')
            print(f'Número de teléfono: {phone_number}')
        if phone_number == None:
            if contact_link == None:
                print('No se encontraron números de teléfono en la página web.')
            else:
                #por si el url no es completo, se agrega el dominio a la url para obtener el correo de la pagina de contacto
                if not contact_link.startswith('http'):
                    base_url = urlparse(link)
                    complete_contact_link = f"{base_url.scheme}://{base_url.netloc}{contact_link}"
                    phone_number_and_text = get_tlf(complete_contact_link)
                    
                else:
                    #url completa antes, no hace falta agragar nada
                    phone_number_and_text = get_tlf(contact_link)
                if phone_numbers_and_text == None:
                    print('No se encontraron números de teléfono en la página web.')
                else:
                    for item in phone_numbers_and_text:
                        text, phone_number = item

                        print(f' {text} ')
                        print(f'Número de teléfono: {phone_number}')
    else:
        print('No se encontraron números de teléfono en la página web.')

except (HTTPError) as e:
    print(f'Error no hay pagina de contacto: {e}')


    