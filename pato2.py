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
# soup = bs(html.text, 'html.parser')

# # email = soup.find('div', class_='office col-md-5')
# # Encontrar el elemento <a> con la clase '__cf_email__'
# a_tag = soup.find('a', class_='__cf_email__')

# # Obtener el valor del atributo 'data-cfemail'
# fp = a_tag['data-cfemail']

# # Imprimir el valor de cfemail
# print("Valor de data-cfemail:", fp)
# def deCFEmail(fp):
#         try:
#             r = int(fp[:2],16)
#             email = ''.join([chr(int(fp[i:i+2], 16) ^ r) for i in range(2, len(fp), 2)])
#             return email
#         except (ValueError):
#             pass

# print(deCFEmail(fp))



# Seleccionar el div por su clase
mi_div = soup.find('div', class_='VwiC3b yXK7lf lyLwlc yDYNvb W8l4ac lEBKkf')
texto_sin_fecha = mi_div.get_text().split('—', 1)[-1].strip()
print(texto_sin_fecha)
# Obtener la etiqueta span dentro del div
mi_span = mi_div.find('span')
if len(mi_span.find_all()) == 1:
    # No contiene etiquetas adicionales, por lo tanto, no tiene más etiquetas
    texto_del_span = mi_span.text
    print(texto_del_span)
# Obtener el texto dentro de la etiqueta span
