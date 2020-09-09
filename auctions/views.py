from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.forms import ModelForm
from django import forms

from .models import User, ListingPage, Biddings

@login_required(login_url='login')
def index(request):
    return render(request, "auctions/index.html", {
        "listings": ListingPage.objects.all()
    })

class NewListing(ModelForm):

    class Meta:
        model = ListingPage
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['user'].initial = self.user

@login_required(login_url='login')
def new_listing(request):

    form = NewListing(user=request.user)

    if request.method == 'POST':
        form = NewListing(request.POST, user=request.user)

        if form.is_valid():
            form.save(commit=True)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/new_listing.html", {
                'form': form,
                'error_message': "Cannot create new listing. Please try again."
            })
    return render(request, "auctions/new_listing.html", {
                'form': form
    })

class NewBidding(forms.Form):
    bid_price = forms.IntegerField()

@login_required(login_url='login')
def listing(request, listing_id):
    user = request.user
    listing = ListingPage.objects.get(id=listing_id)
    biddings = Biddings.objects.filter(item_id=listing_id)
    num_of_bids = len(biddings)
    bid_form = NewBidding()
    return render(request, 'auctions/listing.html', {
        "listing": listing,
        "biddings": biddings,
        "user": user,
        "numofbids": num_of_bids,
        "form": bid_form
    })



@login_required(login_url='login')
def bidding(request, listing_id):
    user = request.user
    if request.method == 'POST':
        max_bid = Biddings.objects.filter(item_id=listing_id).values('bidding').last()
        bid_form = NewBidding(request.POST)
        if bid_form.is_valid():
            bid_price = int(bid_form.cleaned_data['bid_price'])
            if max_bid is None:
                startbid = ListingPage.objects.filter(id=listing_id).values('startbids').first().get('startbids')
                if bid_price <= startbid:
                    return HttpResponseRedirect(reverse("listing", args=[listing_id]))
                else:
                    new_bid = Biddings(item_id=ListingPage.objects.get(id=listing_id), bidder=User.objects.get(username=user), bidding=bid_price)
                    new_bid.save()
                    return HttpResponseRedirect(reverse("listing", args=[listing_id]))
            elif not max_bid is None:
                if bid_price <= max_bid:
                    return HttpResponseRedirect(reverse("listing", args=[listing_id]))
                else:
                    new_bid = Biddings(item_id=ListingPage.objects.get(id=listing_id), bidder=User.objects.get(username=user), bidding=bid_price)
                    new_bid.save()
                    return HttpResponseRedirect(reverse("listing", args=[listing_id]))


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
