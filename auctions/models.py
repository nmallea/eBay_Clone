from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import math
from django.db import models
from django.db.models import Max


class User(AbstractUser):
    watchlist = models.ManyToManyField(
        "Listing", blank=True, related_name="user_watch"
    )

class Listing(models.Model):
    ACTIVE = "A"
    CLOSED = "C"

    MEDIA = "M"
    SPORTS = "S"
    CLOTHING = "C"
    HOUSEHOLD = "H"
    VEHICLES = "V"
    PETS = "P"
    ANTIQUES = "A"

    CATEGORY_CHOICES = [
        (MEDIA, "Electronics & Games"),
        (SPORTS, "Sport & Recreation"),
        (CLOTHING, "Clothing & Accessories"),
        (HOUSEHOLD, "Home & Garden"),
        (VEHICLES, "Cars & Trucks"),
        (PETS, "Pets & Accessories"),
        (ANTIQUES, "Antiques & Rare"),
    ]

    STATUS = [
        (ACTIVE, "Active"),
        (CLOSED, "Closed")
    ]

    title = models.CharField(max_length=64)
    category = models.CharField(max_length=1, choices=CATEGORY_CHOICES, default=MEDIA)
    min_bid = models.DecimalField(
        max_digits=7, decimal_places=2, default=0,
        validators=[MinValueValidator(1, message="Bid must be $1 or greater")]
        )
    description = models.TextField(max_length=1000)
    image_url = models.URLField(max_length=300, blank=True)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="listing_owner"
        )
    status = models.CharField(max_length=1, choices=STATUS, default=ACTIVE)
    listing_date = models.DateTimeField(auto_now=True)

    def timestamp(self):
        now = timezone.now()
        diff = now - self.listing_date

        if diff.days == 0 and diff.seconds >= 0 and diff.seconds < 60:
            seconds = diff.seconds

            if seconds == 1:
                return str(seconds) +  "second ago"

            else:
                return str(seconds) + " seconds ago"

        if diff.days == 0 and diff.seconds >= 60 and diff.seconds < 3600:
            minutes= math.floor(diff.seconds/60)

            if minutes == 1:
                return str(minutes) + " minute ago"

            else:
                return str(minutes) + " minutes ago"

        if diff.days == 0 and diff.seconds >= 3600 and diff.seconds < 86400:
            hours= math.floor(diff.seconds/3600)

            if hours == 1:
                return str(hours) + " hour ago"

            else:
                return str(hours) + " hours ago"

        # 1 day to 30 days
        if diff.days >= 1 and diff.days < 30:
            days= diff.days

            if days == 1:
                return str(days) + " day ago"

            else:
                return str(days) + " days ago"

        if diff.days >= 30 and diff.days < 365:
            months= math.floor(diff.days/30)


            if months == 1:
                return str(months) + " month ago"

            else:
                return str(months) + " months ago"

        if diff.days >= 365:
            years= math.floor(diff.days/365)

            if years == 1:
                return str(years) + " year ago"

            else:
                return str(years) + " years ago"

    def __str__(self):
        return f"{self.title} ({self.owner.username})"

    def top_bid(self):
        try:
            amount = 0
            top_bid = None
            for bid in self.bid_listing.all():
                if int(bid.bid) > int(amount):
                    amount = bid.bid
                    top_bid = bid
            return top_bid
        except ValueError:
            return None

class Bid(models.Model):
    bid = models.DecimalField(max_digits=6, decimal_places=0, default=0)
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="bid_owner"
    )
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name="bid_listing",
        default=1
    )
    bid_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.bid}"

    def timestamp(self):
        now = timezone.now()
        diff = now - self.bid_date

        if diff.days == 0 and diff.seconds >= 0 and diff.seconds < 60:
            seconds = diff.seconds

            if seconds == 1:
                return str(seconds) +  "second ago"

            else:
                return str(seconds) + " seconds ago"

        if diff.days == 0 and diff.seconds >= 60 and diff.seconds < 3600:
            minutes= math.floor(diff.seconds/60)

            if minutes == 1:
                return str(minutes) + " minute ago"

            else:
                return str(minutes) + " minutes ago"

        if diff.days == 0 and diff.seconds >= 3600 and diff.seconds < 86400:
            hours= math.floor(diff.seconds/3600)

            if hours == 1:
                return str(hours) + " hour ago"

            else:
                return str(hours) + " hours ago"

        # 1 day to 30 days
        if diff.days >= 1 and diff.days < 30:
            days= diff.days

            if days == 1:
                return str(days) + " day ago"

            else:
                return str(days) + " days ago"

        if diff.days >= 30 and diff.days < 365:
            months= math.floor(diff.days/30)


            if months == 1:
                return str(months) + " month ago"

            else:
                return str(months) + " months ago"

        if diff.days >= 365:
            years= math.floor(diff.days/365)

            if years == 1:
                return str(years) + " year ago"

            else:
                return str(years) + " years ago"

class Comment(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="cmt_listing")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cmt_owner")
    title = models.CharField(max_length=64)
    message = models.CharField(max_length=400)
    cmt_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['cmt_date']

    def __str__(self):
        return f"{self.title}, {self.owner.username}"
