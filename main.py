import time
import re
from bs4 import BeautifulSoup
from selenium import webdriver
import os
from dotenv import load_dotenv
from telegram import Bot
import asyncio

load_dotenv()

async def send_photo(path):
    with open(path, 'rb') as file:
        await bot.send_photo(chat_id=os.getenv('CHAT_ID'), photo=file)

def contains_in_list(element, list):
    for list_element in list:
        if element == list_element:
            return True
    return False

options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)

bot = Bot(token=os.getenv("BOT_TOKEN"))

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

    asyncio.run(send_photo(path))

    print("copied")
else:
    for bet_id in bets_ids:
        if not contains_in_list(bet_id, previous_bets_ids):
            print("not contains!" + bet_id)
            previous_bets_ids.append(bet_id)
            driver.save_screenshot(path)

            asyncio.run(send_photo(path))

for bet_id in previous_bets_ids:
    print(bet_id)

driver.refresh()

#Конец цикла

print("end")
time.sleep(5)
driver.close()
