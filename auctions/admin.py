from django.contrib import admin

from .models import Categories, ListingPage, User, Biddings

# Register your models here.
admin.site.register(User)
admin.site.register(Categories)
admin.site.register(ListingPage)
admin.site.register(Biddings)