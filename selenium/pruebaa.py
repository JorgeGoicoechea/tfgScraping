#no es capaz de funcionar, creo que porque los buscadores lo tienen bastante parcheao
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementNotInteractableException
from bs4 import BeautifulSoup
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
import time

def get_company_website(company_name):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.150 Safari/537.36")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://google.com")

    # Esperar hasta que la página se cargue completamente
    time.sleep(5)

    # Ejecutar un script para establecer el valor del campo de búsqueda
    search_term = company_name
    driver.execute_script('document.querySelector("input[name=q]").value = arguments[0]', search_term)

    # Enviar la tecla "Enter" para realizar la búsqueda
    driver.find_element(By.NAME, "q").send_keys(Keys.RETURN)

    time.sleep(30)
    driver.execute_script('document.querySelector("input[name=q]").value = arguments[0]', search_term)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    search_results = soup.find_all('div', class_='tF2Cxc')

    if search_results:
        first_result = search_results[0]
        link = first_result.find('a')
        website = link['href']
        driver.quit()
        return website
    else:
        driver.quit()
        return None

company_name = input("Enter the name of the company: ")
website = get_company_website(company_name)

if website:
    print(f"The website of {company_name} is: {website}")
else:
    print(f"No search results found for {company_name}")
