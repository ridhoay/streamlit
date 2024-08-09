import requests
from bs4 import BeautifulSoup
import datetime
import pandas as pd

# search_query = input("Enter the search query: ")
# search_query_formatted = search_query.replace(' ', '+')
URL = f'https://shopee.co.id/search?keyword=zenbook+14'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
response = requests.get(URL, headers=headers)

if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')
    pretty = BeautifulSoup(soup.prettify(), 'html.parser')
    items = soup.findAll('div', class_="p-2 flex-1 flex flex-col justify-between")
    print(items)

    items_list = []

    for item in soup.findAll('li', class_="col-xs-2-4 shopee-search-item-result__item"):
        name = item.find('div', class_="line-clamp-2 break-words min-h-[2.5rem] text-sm").text.strip()
        print(name)
        # price = item.find('span', class_="text-base/5 truncate").text.strip()
        # items_sold_raw = item.find('div', class_="truncate text-shopee-black87 text-xs min-h-4 flex-shrink-1")
        # items_sold = items_sold_raw.get_text(strip=True) if items_sold_raw else ""
        # date = datetime.date.today()

        # items_list.append((name, price, items_sold, date))

    # column_names = ['Name', 'Price', 'Items Sold', 'Date']
    # df = pd.DataFrame(items_list, columns=column_names)
    # print(df)

else:
    print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
