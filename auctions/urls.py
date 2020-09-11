from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create_listing, name="create_listing"),
    path("listing/<int:listing_id>", views.listing, name="listing"),
    path("watchlist/<str:user_id>", views.watchlist, name="watchlist"),
    path("add_watchlist", views.add_watchlist, name="add_watchlist"),
    path("remove_watchlist", views.remove_watchlist, name="remove_watchlist"),
    path("place_bid", views.place_bid, name="place_bid"),
    path("comment", views.add_comment, name="add_comment"),
    path("close_listing", views.close_listing, name="close_listing"),
    path("my_listing", views.my_listing, name="my_listing"),
    path("all_listing", views.all_listing, name="all_listing"),
    path("category_sort/<str:category>", views.category_sort, name="category_sort")
]
