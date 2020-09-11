from django.contrib import admin
from .models import *

class UserAdmin(admin.ModelAdmin):
    filter_horizontal = ("watchlist", )

class BidAdmin(admin.ModelAdmin):
    list_display = ("bid", "listing", "owner", )

class CommentAdmin(admin.ModelAdmin):
    list_display = ("title", "message", "owner", )

admin.site.register(User, UserAdmin)
admin.site.register(Listing)
admin.site.register(Bid, BidAdmin)
admin.site.register(Comment, CommentAdmin)
