from bs4 import BeautifulSoup
import requests
import json
import datetime
from urllib.request import urlopen
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse, parse_qs
from langdetect import detect

def get_tlf(url):
    try:
        html = urlopen(url)
    except (HTTPError,URLError) as e:
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
        
        # Busca números de teléfono con el formato "(+34) 946 41 51 19" en el contenido HTML
        phone_numbers_in_html = re.findall(r'\(\+\d{1,4}\)\s*\d{3}\s*\d{2}\s*\d{2}\s*\d{2}', visible_text)
        # Agrega la nueva expresión regular para buscar números con el formato "+(34) 984 086 203"
        phone_numbers_in_html += re.findall(r'\+\(\d{2,3}\)\s*\d{3}\s*\d{3}\s*\d{3}', visible_text)
        # Agrega la nueva expresión regular para buscar números con el formato "+33 (0)7 80 98 92 23"
        phone_numbers_in_html += re.findall(r'\+\d{2,3}\s*\(\d\)\s*\d{1,2}[\s\d]*', visible_text)
        # Agrega la nueva expresión regular para buscar números con el formato "(+34) 946.855.710"
        phone_numbers_in_html += re.findall(r'\(\+\d{2,3}\)\s*\d{3}.\d{3}.\d{3}', visible_text)


        
        for phone_number in phone_numbers_in_html:
            formatted_number = phone_number.replace('(', '').replace(')', '').replace(' ', '')
            if formatted_number not in [phone for (_, phone) in phone_numbers_with_text]:
                phone_numbers_with_text.append(('', formatted_number))
    
    except AttributeError as e:
        return None
    
    return phone_numbers_with_text


# URL de la página web que deseas analizar
url = 'https://alen.space/es/inicio/'

# Llama a la función y obtén la lista de números de teléfono y su texto precedente
phone_numbers_and_text = find_phone_numbers_and_text(url)

# Imprime los números de teléfono y su texto precedente
if phone_numbers_and_text:
    for item in phone_numbers_and_text:
        text, phone_number = item
        print(f'Texto precedente: {text}')
        print(f'Número de teléfono: {phone_number}')
else:
    print('No se encontraron números de teléfono en la página web.')