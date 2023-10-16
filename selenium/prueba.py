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

    wait = WebDriverWait(driver, 30)
    try:
        search_bar = driver.find_element(By.NAME, "q")
        driver.execute_script("arguments[0].scrollIntoView();", search_bar)
        search_bar = wait.until(EC.element_to_be_clickable((By.NAME, "q")))
        # Scroll to the element
        actions = ActionChains(driver)
        actions.move_to_element(search_bar).perform()
        search_bar.send_keys(company_name)
        search_bar.send_keys(Keys.RETURN)
    except ElementNotInteractableException:
        print("search bar not interactable")

        time.sleep(10)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        search_results = soup.find_all('div', class_='yuRUbf')

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


# # Set up Selenium webdriver
# ChromeOptions options = new ChromeOptions()
# options.addArguments("start-maximized"); # open Browser in maximized mode
# options.addArguments("disable-infobars"); #disabling infobars
# options.addArguments("--disable-extensions"); # disabling extensions
# options.addArguments("--disable-gpu"); # applicable to windows os only
# options.addArguments("--disable-dev-shm-usage"); # overcome limited resource problems
# options.addArguments("--no-sandbox"); # Bypass OS security model
# WebDriver driver = new ChromeDriver(options)
# driver.get("https://google.com")
# service = Service('/usr/local/bin/chromedriver')
# driver = webdriver.Chrome(service=service)
# driver.get("https://www.google.com")

# # Find the search bar and enter the company name
# search_bar = driver.find_element_by_name("q")
# company_name = input("Enter the name of the company: ")
# search_bar.send_keys(company_name + Keys.RETURN)

# # Wait for the search results to load
# driver.implicitly_wait(5)

# # Get the page source and create a BeautifulSoup object
# page_source = driver.page_source
# soup = BeautifulSoup(page_source, "html.parser")

# # Find the first search result and extract the website URL
# search_result = soup.find("div", class_="yuRUbf")
# website_url = search_result.a["href"]

# print("Website URL:", website_url)

# # Close the browser
# driver.quit()