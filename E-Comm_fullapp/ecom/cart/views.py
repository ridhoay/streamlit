from django.shortcuts import render, get_object_or_404
from .cart import Cart
from store.models import Product
from django.http import JsonResponse


# Create your views here.
def cart_summary(request):
    cart = Cart(request)
    cart_products = cart.get_prods()  
    return render(request, 'cart_summary.html', {"cart_products": cart_products})

def cart_add(request):
    # Get the cart
    cart = Cart(request)
    # Test for POST
    if request.POST.get('action') == 'post':
        # Get product ID
        product_id = int(request.POST.get('product_id'))
        # Get the product
        product = get_object_or_404(Product, id=product_id)
        # Add to cart
        
        # Get cart quantity
        cart_quantity = cart.__len__()

        cart.add(product=product)
        # Return JSON response
        return JsonResponse({'qty': cart_quantity})

def cart_remove(request):
    pass

def cart_update(request):
    pass