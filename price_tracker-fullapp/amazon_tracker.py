# import libraries 

from bs4 import BeautifulSoup
import requests
import time
import datetime

import smtplib


# URL = 'https://www.amazon.com/Funny-Data-Systems-Business-Analyst/dp/B07FNW9FGJ/ref=sr_1_3?dchild=1&keywords=data%2Banalyst%2Btshirt&qid=1626655184&sr=8-3&customId=B0752XJYNL&th=1'
URL = 'https://www.amazon.com/s?k=lamzu+atlantis&crid=3DZMGJO3G9EP0&sprefix=lamzu+atlantis%2Caps%2C322&ref=nb_sb_noss_1'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

response = requests.get(URL, headers=headers)

if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')
    print(soup)    
    
else:
    print(f"Failed to retrieve the webpage. Status code: {response.status_code}")

# soup1 = BeautifulSoup(page.content, "html.parser")
# soup2 = BeautifulSoup(soup1.prettify(), "html.parser")

# title = soup2.find(id='productTitle').get_text()
# price = soup2.find(id='priceblock_ourprice').get_text()


# print(title)
# print(price)