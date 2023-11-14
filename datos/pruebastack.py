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
        #antes llamada con urllib no request
        #arreglar error 406
        #arreglar error 403

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
    

#funcion obtiene los idiomas de la pagina web
def get_idiomas(url):
    try:
        #antes llamada con urllib no request
        #arreglar error 406
        #arreglar error 403
        req = Request(url, headers=headers)
        html = urlopen(req)
    except (HTTPError,URLError) as e:
         print(f'Error en get_idiomas: {e}')
         return None
    try:
         bsObject = BeautifulSoup(html, 'html.parser')
         # Busca todas las etiquetas 'link' con atributo 'hreflang', justo son las de los idiomas de todas las paginas
         hreflang_tags = bsObject.find_all('link', {'rel': 'alternate', 'hreflang': re.compile('.*', re.I)})
         # Busca etiquetas <a> que contienen el atributo 'lang' para el idioma
         a_lang_tags = bsObject.find_all('a', {'lang': re.compile('.*', re.I)})

    except AttributeError as e:
         return None
    idiomas = []
    if hreflang_tags:
         # Itera sobre las etiquetas y obtén los valores de 'hreflang', esa etiqueta es la que tiene el idioma
         for tag in hreflang_tags:
            hreflang_value = tag['hreflang']
            if len(hreflang_value) <= 4:
                idiomas.append(hreflang_value)
    #mirar todos lo <a lang>
    else:
        if a_lang_tags:
            # Itera sobre las etiquetas <a> y obtén los valores del atributo 'lang'
            for tag in a_lang_tags:
                lang_value = tag.get('lang')
                if lang_value:
                    idiomas.append(lang_value)
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
    return idiomas

def get_social_media(url):
    try:
        req = Request(url, headers=headers)
        html = urlopen(req)
    except (HTTPError, URLError) as e:
        print(f'Error en get_social_media: {e}')
        return None

    bsObject = BeautifulSoup(html, 'html.parser')

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


#devuelve el correo que esta protegido por cifrado de cloudfare google
def deCFEmail(fp):
    try:
        r = int(fp[:2],16)
        email = ''.join([chr(int(fp[i:i+2], 16) ^ r) for i in range(2, len(fp), 2)])
        return email
    except (ValueError):
        pass

#funcion obtiene los emails de la pagina web
def get_email(url):
    try:
        #antes llamada con urllib no request
        #arreglar error 406
        #arreglar error 403
        req = Request(url, headers=headers)
        html = urlopen(req)
    except (HTTPError, URLError) as e:
        print(f'Error en get_email: {e}')
        return None
    try:
        bsObj = BeautifulSoup(html, 'html.parser')
        # Utiliza expresión regular para obtener correos de enlaces 'mailto:'
        email_links = bsObj.find('a', href=re.compile(r'^mailto:\b[\w\.-]+@[\w\.-]+\.\w{1,4}\b', re.I))
        fp = None
        if email_links:
            email_links = email_links.get('href').replace('mailto:', '')
            return email_links
        # Si no se encuentran correos en enlaces 'mailto:', busca correos escritos en el contenido visible de la página web,aunque muchas veces no se puede porque esta protegido
        visible_text = bsObj.get_text()
        email_in_text = re.findall(r'\b[\w\.-]+@[\w\.-]+\.\w{1,4}\b', visible_text)
        # Si se encuentran correos en el texto, devuelve el primero, 
        if email_in_text:
            return email_in_text[0]
        #decodificar CloudFare anti scraping protection de email para correo que son visibles en la pagina web <span><a class="__cf_email__" data-cfemail="11787f777e517e62707f74727e7f62647d65787f763f727e7c" href="/cdn-cgi/l/email-protection">[email protected]</a></span>
        # Encontrar el elemento <a> con la clase '__cf_email__'
        a_tag = bsObj.find('a', class_='__cf_email__')
        # Obtener el valor del atributo 'data-cfemail'
        if a_tag:
            fp = a_tag['data-cfemail']
        # devolver valor email decodificado que esta en la etiqueta fp
        if fp:
            email_in_text = deCFEmail(fp)
            return email_in_text
        # Convertir el HTML completo en una cadena de texto
        # html_text = str(bsObj)
        # # Crear una expresión regular que coincida con correos electrónicos
        # email_pattern = re.compile(r'\b[\w\.-]+@[\w\.-]+\.\w{2,3}\b')
        # # Buscar correos electrónicos que coincidan con el patrón en el HTML
        # found_emails = re.findall(email_pattern, html_text)
        # if found_emails:
        #     return found_emails
        # Si no se encuentra ningún correo, devuelve None
        return None
    except AttributeError as e:
        return None
    
#elimina los duplicados, el problema esa si el numero despues del sufijo era el mismo entonces si
#si hay numero igual +34 y sin +34 pasaba los dos, con esta funcion elimina prejijo y compara
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
        #antes llamada con urllib no request
        #arreglar error 406
        #arreglar error 403
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
    #llamada para imprimir los idiomas que tenemos en la pagina web
    idiomas = get_idiomas(link)
    if idiomas is None:
        print('No se encontraron idiomas en la página web.')
    else:
        print(f'idiomas: {idiomas}')

    #llamada para imprimir los correos de la pagina web, del inicio o de la pagina de contacto
    email = get_email(link)
    #si email es NoNe miramos contacto_link para llamar a la funcion para obtener el correo de la pagina de contacto
    if email is None:
        #mirar contact link es None
        if contact_link is None:
            print('No se encontró una dirección de correo electrónico en la página web.')
            #si contact link no es None, llamamos a la funcion para obtener el correo de la pagina de contacto
        else:
            if contact_link is not None:
                #por si el url no es completo, se agrega el dominio a la url para obtener el correo de la pagina de contacto
                if not contact_link.startswith('http'):
                    #nos falta una /porque no se agrega el dominio a la url asi que la añadimos
                    if not contact_link.startswith('/'):
                        base_url = urlparse(link)
                        complete_contact_link = f"{base_url.scheme}://{base_url.netloc}/{contact_link}"
                        email = get_email(complete_contact_link)
                    else:
                        #hay / de por si
                        base_url = urlparse(link)
                        complete_contact_link = f"{base_url.scheme}://{base_url.netloc}{contact_link}"
                        email = get_email(complete_contact_link)
                #la url es completa asi que llamamos directamente a la funcion para obtener el correo de la pagina de contacto
                else:
                    email = get_email(contact_link)
                #como el correo es None, imprimimos que no se encontró un correo en la pagina web o devolvemos el correo si no
                if email is None:
                    print('No se encontró una dirección de correo electrónico en la página web.')
                else:
                    print(f'Dirección de correo electrónico: {email}')
    else:
        print(f'Dirección de correo electrónico: {email}')

    # Llama a la función y obtén la lista de números de teléfono o de la página de contacto

    phone_number = get_tlf(link)
    # si en la pagina de inicio hay Imprime los números de teléfono 
    if phone_number:
        for phone in phone_number:
            print(f'Número de teléfono: {phone}')
    if not phone_number:
        #si no hay números de teléfono, miramos contact link para llamar a la funcion para obtener los números de teléfono de la pagina de contacto
        if contact_link is None:
            print('No se encontraron números de teléfono en la página web.')
        else:
             #por si el url no es completo, se agrega el dominio a la url para obtener el correo de la pagina de contacto
            if not contact_link.startswith('http'):
                #nos falta una /porque no se agrega el dominio a la url asi que la añadimos
                if not contact_link.startswith('/'):
                    base_url = urlparse(link)
                    complete_contact_link = f"{base_url.scheme}://{base_url.netloc}/{contact_link}"
                    phone_number = get_tlf(complete_contact_link)
                else:
                    base_url = urlparse(link)
                    complete_contact_link = f"{base_url.scheme}://{base_url.netloc}{contact_link}"
                    phone_number = get_tlf(complete_contact_link)
            else:
                #la url es completa asi que llamamos directamente a la funcion para obtener  de la pagina de contacto
                phone_number = get_tlf(contact_link)
            if not phone_number:
                print('No se encontraron números de teléfono en la página web.')
            else:
                for phone in phone_number:
                    print(f'Número de teléfono: {phone}')
    #llamada obtener los url de Linkedin y twitter para poder scrapear las dos paginas
    social_media_urls = get_social_media(link)

    if social_media_urls:
        linkedin_url, twitter_url = social_media_urls
        print(f'LinkedIn URL: {linkedin_url}')
        print(f'Twitter URL: {twitter_url}')
    else:
        print('No se encontraron enlaces de LinkedIn ni de Twitter.')


except (HTTPError) as e:
    print(f'problema pagina de contacto: {e}')


    