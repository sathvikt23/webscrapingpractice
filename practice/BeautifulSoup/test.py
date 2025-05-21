import requests
from bs4 import BeautifulSoup

url = "https://www.amazon.in/Taj-2-Strong-Double-Brackets-Curtain/dp/B07C5QCF8L/?_encoding=UTF8&ref_=pd_hp_d_atf_ci_mcx_mr_ca_hp_atf_d"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ",
    "Accept-Language": "en-US,en;q=0.9"
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")
data =soup.find("p",{"id":"pqv-price-list-price"}).find("span",{"class":"a-text-strike"}).text
print(data)
for i in soup.find_all("p"):
    if "List Price" in str(i):
        print(i)