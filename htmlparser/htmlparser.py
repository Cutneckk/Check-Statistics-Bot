from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from seleniumwire import webdriver
from dotenv import load_dotenv
import os
import re

load_dotenv()

PROXY_HOST = os.getenv('PROXY_HOST')
PROXY_PORT = os.getenv('PROXY_PORT')
PROXY_USER = os.getenv('PROXY_USER')
PROXY_PASS = os.getenv('PROXY_PASS')

yam_url = 'https://music.yandex.ru/artist/12886919'
spotify_url = 'https://open.spotify.com/artist/20Z8lq6G4TWfIhXGhrVRf3'


def check_listeners_yam():
    chrome_options = Options()
    chrome_options.add_argument('--headless')

    with webdriver.Chrome(options=chrome_options) as driver:
        driver.get(yam_url)
        l_yam = driver.find_element(By.XPATH,"//*[contains(@class, 'PageHeaderArtist_label__')]")
    listeners_yam = l_yam.find_elements(By.TAG_NAME, "span")

    text = listeners_yam[0].text
    numbers = re.findall(r'\d+', text)
    count = int(''.join(numbers))

    return count


def check_listeners_spotify():
    proxy_options = {
        'proxy': {
            'http': f'http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}',
            'https': f'http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}',
            'no_proxy': 'localhost,127.0.0.1'
        }
    }
    chrome_options = Options()
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--headless')

    with webdriver.Chrome(options=chrome_options,seleniumwire_options=proxy_options) as driver:
        driver.get(spotify_url)
        wait = WebDriverWait(driver, 60)
    listeners_spotify = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "span[class='VmDxGgs77HhmKczsLLBQ']")))
    text = listeners_spotify.text
    numbers = re.findall(r'\d+', text)
    count = int(''.join(numbers))

    return count












