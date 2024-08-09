from django.contrib import admin
from . models import TodoItem, ScrapedItem, Club, PriceTrackerUser

# Register your models here.
admin.site.register(TodoItem)
admin.site.register(ScrapedItem)
admin.site.register(Club)
admin.site.register(PriceTrackerUser)

