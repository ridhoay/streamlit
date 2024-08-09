from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from . models import TodoItem, ScrapedItem
from django.db.models import OuterRef, Subquery, Max
from django.utils import timezone
import requests
from bs4 import BeautifulSoup
import datetime
import json
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction

def home(request):
    if request.method == 'POST':
        item = request.POST.get('item')
        return redirect(f'/search?q={item}')
    return render(request, 'home.html')


def search_results(request):
    search_query = request.GET.get('q')
    if search_query:
        search_query_formatted = search_query.replace(' ', '+')
        url = f'https://www.tokopedia.com/search?q={search_query_formatted}'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            items_dict = {}

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
                items_sold_formatted = items_sold.replace(" terjual", '')
                date = datetime.date.today()
                link = item['href']

                items_dict[name] = {
                    'price': price,
                    'items_sold': items_sold_formatted,
                    'date': date,
                    'link': link,
                    'url': url
                }
            # print(items_dict)
            items_dict = sorted(items_dict.items(), key=lambda x: x[1]['date'], reverse=True)
            return render(request, 'results.html', {'items_dict': items_dict})

        return HttpResponse("Failed to retrieve data from Tokopedia.")

    return redirect('home')


def delete_item(request, item_id):
    if request.method == 'POST':
        item = get_object_or_404(ScrapedItem, id=item_id)
        ScrapedItem.objects.filter(name=item.name, link=item.link).delete()
        return redirect('tracked_items_view')
    return HttpResponse('<h1>Invalid request</h1>', status=400)


def todos(request):
    items = TodoItem.objects.all()
    return render(request, 'todos.html', {'todos': items})


def chart_view(request):
    return render(request, 'chart.html')


def price_history(request, item_id):
    item = get_object_or_404(ScrapedItem, id=item_id)
    price_history = ScrapedItem.objects.filter(name=item.name, link=item.link).order_by('date')

    dates = [entry.date.strftime('%Y-%m-%d') for entry in price_history]
    prices = [float(entry.price.replace('Rp', '').replace('.', '').replace(',', '.')) for entry in price_history]

    context = {
        'item_name': item.name,
        'dates': json.dumps(dates),
        'prices': json.dumps(prices),
    }

    return render(request, 'price_history.html', context)


@login_required
def track_price(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        price = request.POST.get('price')
        items_sold = request.POST.get('items_sold')
        link = request.POST.get('link')
        url = request.POST.get('url')

        if name and price:
            # Create a new ScrapedItem object with the tracked item details
            tracked_item = ScrapedItem(
                name=name,
                price=price,
                items_sold=items_sold,
                date=datetime.date.today(),
                link=link,
                url=url,
                owner=request.user  # Assign the current user as the owner
            )
            tracked_item.save()
            return redirect('tracked_items_view')
    return HttpResponse('<h1>Invalid request</h1>', status=400)


@login_required
def tracked_items_view(request):
    # Subquery to get the latest id for each unique (name, link) combination
    latest_ids_subquery = ScrapedItem.objects.filter(
        name=OuterRef('name'),
        link=OuterRef('link'),
        owner=request.user  # Filter items by the current user
    ).order_by('-date').values('id')[:1]

    # Main query to get items with ids from the subquery
    latest_items = ScrapedItem.objects.filter(
        id__in=Subquery(latest_ids_subquery)
    ).exclude(price="N/A")

    return render(request, 'tracked_items.html', {'tracked_items': latest_items})


@login_required
def update_price(request, item_id):
    if request.method == 'POST':
        item = get_object_or_404(ScrapedItem, id=item_id)
        if item:
            url = item.link
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                              '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                current_price = (soup.find('div', {'data-testid': 'lblPDPDetailProductPrice'})).text

                new_item = ScrapedItem(
                    name=item.name,
                    price=current_price,
                    items_sold=item.items_sold,
                    date=timezone.now(),
                    link=item.link,
                    url=item.url,
                    owner=request.user
                )
                new_item.save()

                # Inside the update_price view function
                messages.success(request, 'Item successfully updated')

                # Redirect to a page after adding the new item
                return redirect('tracked_items_view')

            return HttpResponse("Failed to retrieve data from item.")

        return redirect('tracked_items_view')

    return HttpResponse('<h1>Invalid request</h1>', status=400)


@login_required
@transaction.atomic
def update_all_prices(request):
    if request.method == 'POST':
        items = ScrapedItem.objects.filter(owner=request.user)
        done_items = set()

        for item in items:
            url = item.link
            if url not in done_items:
                done_items.add(url)
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                                  '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                response = requests.get(url, headers=headers)

                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    price_element = soup.find('div', {'data-testid': 'lblPDPDetailProductPrice'})

                    if price_element:
                        current_price = price_element.text.strip()

                        new_item = ScrapedItem(
                            name=item.name,
                            price=current_price,
                            items_sold=item.items_sold,
                            date=timezone.now(),
                            link=item.link,
                            url=item.url,
                            owner=request.user
                        )
                        new_item.save()
                    else:
                        messages.error(request, f'Price element not found for item: {item.name}')
                else:
                    messages.error(request, f'Failed to update item: {item.name}')

        messages.success(request, 'All items successfully updated')
        return redirect('tracked_items_view')

    return HttpResponse('<h1>Invalid request</h1>', status=400)
