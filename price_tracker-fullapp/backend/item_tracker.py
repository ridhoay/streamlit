import requests
from bs4 import BeautifulSoup
import datetime
import pandas as pd


search_query = input("Enter the search query: ")
search_query_formatted = search_query.replace(' ', '+')
# URL = f'https://www.tokopedia.com/search?q={search_query_formatted}'
URL = f'https://www.tokopedia.com/search?q=vxe+r1'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
response = requests.get(URL, headers=headers)

if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')
    items_list = []

    for item in soup.findAll('a', class_="YAEeaDkUOUIxPzURz6noDQ== dJdJ2prDIDmuzfoO5m58aA=="):
        name = item.find('span', class_="_4zuh5-h5tURvY6WpuPWQdA==").text.strip()

        price_elem_1 = item.find('div', class_="KQib-amemtBlmDeX02RD6Q== b4ARHNPOqYx4DIh2XZjC0A==")
        price_elem_2 = item.find('div', class_="KQib-amemtBlmDeX02RD6Q== ")

        if price_elem_1:
            price = price_elem_1.text.strip()
        elif price_elem_2:
            price = price_elem_2.text.strip()
        else:
            price = "N/A"

        items_sold_raw = item.find('span', class_="aaTL4-SKhSwIxU9cUoVD4w==")
        items_sold = items_sold_raw.get_text(strip=True) if items_sold_raw else ""

        location = item.find('span', class_="kN1WCykMRfoX40+JjPBCKg== flip").text.strip()
        date = datetime.date.today()
        link = item['href']

        items_list.append((name, price, items_sold, location, date, link))

    column_names = ['Name', 'Price', 'Items Sold', 'Location', 'Date', 'Link']
    df = pd.DataFrame(items_list, columns=column_names)
    print(df)
    print(items_list[0][1])

else:
    print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
