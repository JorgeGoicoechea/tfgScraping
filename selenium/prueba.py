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
import getpass as gp

# Especifica la ubicación del controlador de Chrome como una opción
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("webdriver.chrome.driver=/usr/local/bin/chromedriver")

# Crea el controlador de Chrome con las opciones
driver = webdriver.Chrome(options=chrome_options)

# # Navega a la página de inicio de sesión de Twitter
driver.get('https://www.twitter.com/login')
# empresa = input("empresa: ")
valor ="elon musk"
time.sleep(3)
# #meter dato de usuario y darle a siguiente
username = driver.find_element(By.XPATH,'//input[@name="text"]')
# prueba = driver.find_element(By.XPATH,'//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[5]/label/div/div[1]/div/span')
# print(prueba.text)
username.send_keys("jorge_goico")
next_button = driver.find_element(By.XPATH,'//span[contains(text(),"Next")]')
next_button.click()
time.sleep(3)
# #meter contraseña y darle a iniciar sesion
# prueba = driver.find_element(By.XPATH,'//*[@id="modal-header"]/span/span')
# print(prueba.text)
password = driver.find_element(By.XPATH,'//input[@name="password"]')
password.send_keys("ak09322000")
log_in_button = driver.find_element(By.XPATH,'//span[contains(text(),"Log in")]')
log_in_button.click()

time.sleep(3)
# #barra de busqueda, meter nombre empresa y darle a enter para buscar 
prueba = driver.find_element(By.XPATH,'/html/body/div[1]/div/div/div[2]/main/div/div/div/div[2]/div/div[2]/div/div/div/div[1]/div/div/div/form/div[1]/div/div/div/label/div[2]/div/input')
print(prueba.text)
wait = WebDriverWait(driver, 10)
search_bar = wait.until(EC.presence_of_element_located((By.XPATH,'//input[@aria-label="Búsqueda"]')))
search_bar.send_keys(valor)
search_bar.send_keys(Keys.ENTER)
time.sleep(3)
# prueba = driver.find_element(By.XPATH,'//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/section/div/div/div[2]/div/div/div/h2/div[2]/span').text
# print(prueba)
# #buscar personas y clickarlo
# people = driver.find_element(By.XPATH,'//span[contains(text(),"People")]')
# people.click()
# time.sleep(3)
# #buscar el perfil de la empresa, primero que aparece y clickarlo
# profile = driver.find_element(By.XPATH,'//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/section/div/div/div[3]/div/div/div/div/div[2]/div/div[1]/div/div[1]/a/div/div[1]/span/span[1]]')
# profile.click()
# profile_tag = profile.find_element(By.XPATH,'//div[@data-testid="User-Name"]').text
# print(profile_tag)
# #cuando ha publicado tweet
# fecha = driver.find_element(By.XPATH,"//time").get_attribute("datetime")
# print(fecha)
# tweet =driver.find_element(By.XPATH,'//div[@data-testid="tweetText"]').text
# print(tweet)