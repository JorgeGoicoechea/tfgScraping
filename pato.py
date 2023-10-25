from bs4 import BeautifulSoup

# Supongamos que este es tu HTML:
html = '<a href="/es/contacto/" target="_self" title=" "> CONTACTO</a>'

# Parsea el HTML con BeautifulSoup
soup = BeautifulSoup(html, 'html.parser')

# Encuentra el elemento <a>
a_tag = soup.find('a')

# Obtiene el valor del atributo "href"
contact_link = a_tag['href']

# Imprime el resultado
print(contact_link)