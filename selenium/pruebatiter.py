from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import time

# Configura el controlador de Chrome
chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(options=chrome_options)

# URL de la página de Twitter
url = "https://twitter.com/Immersia_VR?ref_src=twsrc%5Egoogle%7Ctwcamp%5Eserp%7Ctwgr%5Eauthor"

# Abre la página
driver.get(url)

# Desplázate hacia abajo para cargar más tweets (simulamos presionar la tecla 'END')
body = driver.find_element(By.TAG_NAME, 'body')
for _ in range(10):  # Desplázate hacia abajo 10 veces
    body.send_keys(Keys.END)
    time.sleep(2)  # Espera un momento a que se carguen más tweets

# Obtiene el contenido de la página
page_source = driver.page_source

# Analiza el contenido de la página con BeautifulSoup
soup = BeautifulSoup(page_source, 'html.parser')

tweet_text = soup.find("div", {"id": "id__ubxbkgb58h"})
tweet_text = tweet_text.get_text
print(tweet_text)
# # Encuentra todos los tweets
# tweets = soup.find_all('div', class_='tweet')
# Encuentra el usuario, el timestamp, el tweet y otras métricas
# user_tag = soup.find('div', {'data-testid': 'User-Names'}).get_text()
# timestamp = soup.find('time')['datetime']
# tweet_text = soup.find('div', {'data-testid': 'tweetText'}).get_text()
# reply_count = soup.find('div', {'data-testid': 'reply'}).get_text()
# retweet_count = soup.find('div', {'data-testid': 'retweet'}).get_text()
# like_count = soup.find('div', {'data-testid': 'like'}).get_text()

# Imprime los valores
# print("User:", user_tag)
# print("Timestamp:", timestamp)
# print("Tweet:", tweet_text)
# print("Reply Count:", reply_count)
# print("Retweet Count:", retweet_count)
# print("Like Count:", like_count)
# Itera sobre los tweets y obtén su contenido
# for tweet in tweets:
#     tweet_text = tweet.find('div', class_='js-tweet-text-container').get_text()
#     print(tweet_text)

# Cierra el controlador de Chrome
driver.quit()
