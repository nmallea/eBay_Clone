from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from . models import User, Listing, Bid, Comment
from . forms import ListingForm, BidForm, CommentForm

def index(request):
    listing = Listing.objects.all().filter(status=Listing.active).order_by('-listing_date')
    if request.user.is_authenticated:
        user_watch = User.objects.get(pk=int(request.user.id)).watchlist.all()
        return render(request, "auctions/index.html", {
            "listing": listing,
            "watchlist": user_watch
        })
    return render(request, "auctions/index.html", {
        "listing": listing
    })

@login_required(login_url="/login")
def create_listing(request):
    form = ListingForm(request.POST)
    form.owner = request.user
    if request.method == "POST":
        if form.is_valid():
            try:
                new_listing = form.save(commit=False)
                new_listing.owner = request.user
                new_listing.save()
            except IntegrityError:
                messages.add_message(request, messages.WARNING,
                                     "We were unable to add the listing.")
                return render(request, "auctions/create_listing.html",
                              {"form": form})
            messages.add_message(request, messages.SUCCESS,
                                 "Success! Your listing has been created.")
            return HttpResponseRedirect(reverse("index"))
        messages.add_message(request, messages.WARNING,
                             "Something went wrong. Please try again.")
        return render(request, "auctions/create_listing.html", {"form": form})
    return render(request, 'auctions/create_listing.html', {
        "form": ListingForm()
    })

def listing(request, listing_id):
    list_args = {"listing_id": listing_id,
                 "user_id": request.user.id,
                 "bid_form": None,
                 "cmt_form": None}
    return render(request, "auctions/listing.html",
                  _get_listing_dict(list_args))

def _get_listing_dict(list_args):
    listing_id = list_args["listing_id"]
    user_id = list_args["user_id"]
    user_watchlist = None

    cmt_form = list_args["cmt_form"]
    if cmt_form is None:
        cmt_form = CommentForm()

    bid_form = list_args["bid_form"]
    if bid_form is None:
        bid_form = BidForm()

    try:
        listing = Listing.objects.get(pk=listing_id)
        comments = Comment.objects.get_queryset().filter(listing=listing)
        comment_count = Comment.objects.get_queryset().filter(listing=listing).count()
        bids = Bid.objects.get_queryset().filter(listing=listing).count()
        if user_id:
            user_watchlist = User.objects.get(pk=int(user_id)).watchlist.all()
    except Listing.DoesNotExist:
        raise Http404("Listing not found.")
    except User.DoesNotExist:
        raise Http404("User not found.")
    return {
        "listing": listing,
        "bid_form": bid_form,
        "bids": bids,
        "comments": comments,
        "comment_count": comment_count,
        "cmt_form": cmt_form,
        "watchlist": user_watchlist
    }

@login_required(login_url="/login")
def watchlist(request, user_id):
    try:
        user_watchlist = User.objects.get(pk=int(user_id)).watchlist.all()
    except User.DoesNotExist:
        raise Http404("User not found")
    return render(request, "auctions/all_listing.html", {
        "listings": user_watchlist,
        "watchlist": user_watchlist,
        "category": Listing.category_options
    })

@require_http_methods(["POST"])
@login_required(login_url="/login")
def add_watchlist(request):
    try:
        user = User.objects.get(pk=int(request.user.id))
        selected_listing = Listing.objects.get(pk=int(request.POST["listing_id"]))
        user.watchlist.add(selected_listing)
    except User.DoesNotExist:
        raise Http404("User not found.")
    except Listing.DoesNotExist:
        raise Http404("Listing not found.")
    messages.add_message(request, messages.SUCCESS, "Success! It has been added to the watchlist.")
    return HttpResponseRedirect(reverse("listing", args=(selected_listing.id, )))

@require_http_methods(["POST"])
@login_required(login_url="/login")
def remove_watchlist(request):
    try:
        user = User.objects.get(pk=int(request.user.id))
        selected_listing = Listing.objects.get(pk=int(request.POST["listing_id"]))
        user.watchlist.remove(selected_listing)
    except User.DoesNotExist:
        raise Http404("User not found.")
    except Listing.DoesNotExist:
        raise Http404("Listing not found.")
    messages.add_message(request, messages.SUCCESS, "Success! It has been removed from the watchlist.")
    return HttpResponseRedirect(reverse("listing", args=(selected_listing.id, )))

@require_http_methods(["POST"])
@login_required(login_url="/login")
def place_bid(request):
    top_bid = 0
    try:
        bid_listing = Listing.objects.get(pk=int(request.POST["listing_id"]))
    except Listing.DoesNotExist:
        raise Http404("Listing not found.")

    if bid_listing.top_bid():
        top_bid = int(bid_listing.top_bid().bid)
    form = BidForm(request.POST,
                   min_bid=int(bid_listing.min_bid),
                   top_bid=top_bid)
    if form.is_valid():
        try:
            new_bid = form.save(commit=False)
            new_bid.listing = bid_listing
            new_bid.owner = request.user
            new_bid.save()
        except IntegrityError:
            messages.add_message(request, messages.WARNING,
                                 "We were unable to process your bid. Make sure your bid is higher than current bid.")
            return HttpResponseRedirect(
                reverse("listing", args=(bid_listing.id,)))
        messages.add_message(request, messages.SUCCESS,
                             "Your bid was successful.")
        return HttpResponseRedirect(reverse("listing", args=(bid_listing.id,)))
    messages.add_message(request, messages.WARNING,
                         "We were unable to process your bid. Make sure your bid is higher than current bid.")
    list_args = {"bid_form": form,
                 "cmt_form": None,
                 "listing_id": request.POST["listing_id"],
                 "user_id": request.user.id}
    return render(request, "auctions/listing.html",
                  _get_listing_dict(list_args))

@login_required(login_url="/login")
def add_comment(request):
    form = CommentForm(request.POST)
    form.owner = request.user
    if request.method == "POST":
        if form.is_valid():
            try:
                cmt_listing = Listing.objects.get(pk=int(request.POST["listing_id"]))
                new_cmt = form.save(commit=False)
                new_cmt.listing = cmt_listing
                new_cmt.owner = request.user
                new_cmt.save()
            except IntegrityError:
                messages.add_message(request, messages.WARNING,
                    "Question was not submitted." + "Please try again."
                )
                return HttpResponseRedirect(reverse("listing", args=(cmt_listing.id, )))
            except Listing.DoesNotExist:
                raise Http404("Listing Not Found")
            messages.add_message(request, messages.SUCCESS,
                "Question successfully submitted."
            )
            return HttpResponseRedirect(reverse("listing", args=(cmt_listing.id, )))
        messages.add_message(request, messages.WARNING,
            "We were unable to send your question."
        )

        list_args = {"bid_form": None,
                     "cmt_form": form,
                     "listing_id": request.POST["listing_id"],
                     "user_id": request.user.id
        }
        return render(request, 'auctions/listing.html', {
           _get_listing_dict(list_args)
        })

@require_http_methods(["POST"])
@login_required(login_url="/login")
def close_listing(request):
    try:
        status_listing = Listing.objects.get(pk=int(request.POST["listing_id"]))
        status_listing.status = Listing.closed
        status_listing.save()
    except Listing.DoesNotExist:
        raise Http404("Listiing not found")
    messages.add_message(request, messages.INFO,
        "Auction is now closed"
    )
    return HttpResponseRedirect(reverse("listing", args=(status_listing.id, )))

@login_required(login_url="/login")
def my_listing(request):
    my_listing = Listing.objects.all().filter(owner=request.user.id).order_by('-listing_date')
    try:
        user_watch = User.objects.get(pk=int(request.user.id)).watchlist.all()
    except User.DoesNotExist:
        raise Http404("User not found")
    return render(request, "auctions/my_listing.html", {
        "listings": my_listing,
        "watchlist": user_watch,
        "category": Listing.category_options
    })

def all_listing(request):
    all_listing = Listing.objects.all().order_by('-listing_date')
    if request.user.is_authenticated:
        try:
            user_watch = User.objects.get(pk=int(request.user.id)).watchlist.all()
        except User.DoesNotExist:
            raise Http404("User not found")
        return render(request, "auctions/all_listing.html", {
            "listings": all_listing,
            "watchlist": user_watch,
            "category": Listing.category_options
        })
    return render(request, "auctions/all_listing.html", {
        "listings": all_listing,
        "category": Listing.category_options
    })

def category_sort(request, category):
    listing = Listing.objects.all().filter(category=category, status=Listing.active).order_by('-listing_date')
    return render(request, 'auctions/all_listing.html', {
        "listings": listing,
        "category": Listing.category_options
    })

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

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
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })
        try:
            user = User.objects.create_user(username, email, password, first_name=first_name, last_name=last_name)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
