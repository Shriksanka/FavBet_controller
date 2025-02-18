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

def autorization(driver):
    driver.get("https://www.favbet.ua/uk/login")
    time.sleep(5)

    email_field = driver.find_element("id", "email")
    email_field.send_keys(os.getenv("EMAIL"))

    password_field = driver.find_element("id", "password")
    password_field.send_keys(os.getenv("PASSWORD"))

    enter_button = driver.find_element("css selector", "form> button[data-role='login-page-submit-btn']")
    enter_button.click()

def parse_bets(driver):
    bets_ids = []
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    selector_for_bets = "div.Bet_container--lCz:contains('Невизначено') span[data-role='bets-history-text-copy-id-text']"
    parse_bets = soup.select(selector_for_bets)

    for bet in parse_bets:
        bet_id = re.search("\d+", bet.get_text())
        bets_ids.append(bet_id.group(0))

    return bets_ids

def check_bets(bets_ids, previous_bets_ids):
    if not previous_bets_ids and bets_ids:
        previous_bets_ids.extend(bets_ids)
        driver.save_screenshot(path)
        asyncio.run(send_photo(path))
    else:
        for bet_id in bets_ids:
            if not contains_in_list(bet_id, previous_bets_ids):
                previous_bets_ids.append(bet_id)
                driver.save_screenshot(path)
                asyncio.run(send_photo(path))

options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)

bot = Bot(token=os.getenv("BOT_TOKEN"))

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

#Авторизация
autorization(driver)

time.sleep(5)

driver.get("https://www.favbet.ua/uk/personal-office/bets/sport/")

#Начало цикла

time.sleep(15)

bets_ids = parse_bets(driver)
previous_bets_ids = []
path = "./screenshots/file.png"

#Поиск новых ставок
check_bets(bets_ids, previous_bets_ids)

driver.refresh()

#Конец цикла

print("end")
time.sleep(5)
driver.close()
