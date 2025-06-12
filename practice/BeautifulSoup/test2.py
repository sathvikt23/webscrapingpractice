from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import requests
url = "https://www.harpercollins.ca/9780778387770/a-most-puzzling-murder/"
headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Connection": "keep-alive"
    }

try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"Failed to fetch page: {response.status_code}")
            
except requests.exceptions.RequestException as e:
     print(f"Request failed: {e}")
    

soup = BeautifulSoup(response.text, "html.parser")

img = soup.select("#product-details-16892 > div.book-wrapper.hc-book.hc-container > div.hc-book__left > div.hc-book__cover.hide-mobile > img")
for i in img :
    print(i)
#print(img['src'] if img else "Image not found")

