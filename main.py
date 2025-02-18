import time
import re
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import os
from dotenv import load_dotenv

load_dotenv()

def contains_in_list(element, list):
    for list_element in list:
        if element == list_element:
            return True
    return False

options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)

#Авторизация
driver = webdriver.Chrome(options=options)

driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    'source': '''
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_JSON;
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Object;
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Proxy;
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Window;
    '''
})

driver.get("https://www.favbet.ua/uk/login")
time.sleep(5)

email_field = driver.find_element("id", "email")
email_field.send_keys(os.getenv("EMAIL"))

password_field = driver.find_element("id", "password")
password_field.send_keys(os.getenv("PASSWORD"))

enter_button = driver.find_element("css selector", "form> button[data-role='login-page-submit-btn']")
enter_button.click()
print(enter_button.text)

time.sleep(5)

driver.get("https://www.favbet.ua/uk/personal-office/bets/sport/")
driver.fullscreen_window()

#Начало цикла

time.sleep(5)

soup = BeautifulSoup(driver.page_source, 'html.parser')
selector_for_bets = "div.Bet_container--lCz:contains('Невизначено') span[data-role='bets-history-text-copy-id-text']"
parse_bets = soup.select(selector_for_bets)

bets_ids = []
previous_bets_ids = []
path = "./screenshots/file.png"

for bet in parse_bets:
    bet_id = re.search("\d+", bet.get_text())
    bets_ids.append(bet_id.group(0))

if not previous_bets_ids and bets_ids:
    previous_bets_ids = bets_ids.copy()
    driver.save_screenshot(path)
    #Вызов телеграм бота ?
    print("copied")
else:
    for bet_id in bets_ids:
        if not contains_in_list(bet_id, previous_bets_ids):
            print("not contains!" + bet_id)
            previous_bets_ids.append(bet_id)
            driver.save_screenshot(path)
            #Вызов телеграм бота ?

for bet_id in previous_bets_ids:
    print(bet_id)

driver.refresh()

#Конец цикла

print("end")
time.sleep(5)
driver.close()
