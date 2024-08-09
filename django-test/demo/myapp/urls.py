from django.urls import path
from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("search", views.search_results, name='search_results'),
    path("todos/", views.todos, name="todos"),
    path('track_price/', views.track_price, name='track_price'),
    path("tracked_items/", views.tracked_items_view, name="tracked_items_view"),
    path('delete/<int:item_id>/', views.delete_item, name='delete_item'),
    path('price_history/<int:item_id>/', views.price_history, name='price_history'),
    path("charts/", views.chart_view, name="charts"),
    path('update_price/<int:item_id>/', views.update_price, name='update_price'),
    path('update_all_prices/', views.update_all_prices, name='update_all_prices'),
]
