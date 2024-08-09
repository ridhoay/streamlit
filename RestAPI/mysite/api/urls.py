from django.urls import path
from . import views

urlpatterns = [
    path('blogposts/', views.BlogPostListCreate.as_view(), name='blogposts-view-create'),
    path('blogposts/<int:pk>/', views.BlogPostRetrieveUpdateDestroy.as_view(), name='blogposts-view-retrieve-update-destroy'),
    path('blogposts/all/', views.BlogPostList.as_view(), name='blogposts-all-view'),
]