import time
import re
from bs4 import BeautifulSoup
from selenium import webdriver
import os
from dotenv import load_dotenv
from telegram import Bot
import asyncio
import logging
from logging.handlers import RotatingFileHandler
import datetime


def setup_logging():
    log_folder = "logs"
    os.makedirs(log_folder, exist_ok=True)

    current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = os.path.join(log_folder, f"favbet_script_{current_time}.log")

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        handlers=[
                            RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=3),
                            logging.StreamHandler()
                        ])
    logging.info("✅ Logging setup completed.")

async def send_photo(path):
    with open(path, 'rb') as file:
        await bot.send_photo(chat_id=os.getenv('CHAT_ID'), photo=file)
        logging.info(f"📸 Screenshot sent: {path}")

def contains_in_list(element, list):
    return element in list

def autorization(driver):
    logging.info("🔑 Starting authorization...")
    driver.get("https://www.favbet.ua/uk/login")
    time.sleep(5)

    email_field = driver.find_element("id", "email")
    email_field.send_keys(os.getenv("EMAIL"))
    logging.info("📧 Email entered.")

    password_field = driver.find_element("id", "password")
    password_field.send_keys(os.getenv("PASSWORD"))
    logging.info("🔒 Password entered.")

    enter_button = driver.find_element("css selector", "form> button[data-role='login-page-submit-btn']")
    enter_button.click()
    logging.info("✅ Login button clicked.")

def parse_bets(driver):
    logging.info("🔍 Parsing bets...")
    bets_ids = []
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    selector_for_bets = "div.Bet_container--lCz:contains('Невизначено') span[data-role='bets-history-text-copy-id-text']"
    parse_bets = soup.select(selector_for_bets)

    for bet in parse_bets:
        bet_id = re.search("\d+", bet.get_text())
        bets_ids.append(bet_id.group(0))

    logging.info(f"✅ Found {len(bets_ids)} bets.")

    return bets_ids

def check_bets(bets_ids, previous_bets_ids):
    logging.info("🔄 Checking new bets...")

    if not previous_bets_ids and bets_ids:
        previous_bets_ids.extend(bets_ids)
        driver.save_screenshot(path)
        asyncio.run(send_photo(path))
        logging.info(f"🆕 First bets found: {bets_ids}")
    else:
        for bet_id in bets_ids:
            if not contains_in_list(bet_id, previous_bets_ids):
                previous_bets_ids.append(bet_id)
                driver.save_screenshot(path)
                asyncio.run(send_photo(path))

                logging.info(f"🆕 New bet detected: {bet_id}")

def cloudflare_security_optional(driver):
    logging.info("🛡️ Applying Cloudflare bypass...")
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
    logging.info("✅ Cloudflare security bypass applied.")


if __name__ == "__main__":
    load_dotenv()

    setup_logging()

    logging.info("🚀 Starting Favbet Bot...")

    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    logging.info("🖥️ WebDriver initialized.")
    driver = webdriver.Chrome(options=options)

    cloudflare_security_optional(driver)

    bot = Bot(token=os.getenv("BOT_TOKEN"))

    autorization(driver)
    time.sleep(5)

    logging.info("📄 Navigated to bet history page.")
    driver.get("https://www.favbet.ua/uk/personal-office/bets/sport/")

    # Nachalo cykla

    time.sleep(15)

    bets_ids = parse_bets(driver)
    previous_bets_ids = []
    path = "./screenshots/file.png"

    # Поиск новых ставок
    check_bets(bets_ids, previous_bets_ids)

    logging.info("🔄 Page refreshed.")
    driver.refresh()

    # Конец цикла

    logging.info("🏁 Script execution finished.")
    time.sleep(5)
    driver.close()
    logging.info("❌ WebDriver closed.")
