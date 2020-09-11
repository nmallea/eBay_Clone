from django import forms
from django.forms import ModelForm, Textarea, Select, TextInput, \
    NumberInput, PasswordInput

from .models import *

class ListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = ["title", "category", "min_bid", "description", "image_url"]
        widgets = {
            'title': TextInput(attrs={
                'class': 'form-control mb-2', 'placeholder': 'Required - 64 characters maximum'
            }),
            'category': Select(choices=Listing.CATEGORY_CHOICES, attrs={
                'class': 'form-control', 'id': 'inputGroupSelect01'
            }),
            'min_bid': NumberInput(attrs={
                'class': 'form-control', 'min': '1', 'step': '0.02', 'placeholder': 'Starting Bid (Required)'
            }),
            'description': Textarea(attrs={
                'class': 'form-control mb-2', 'placeholder': 'Required - 1000 character maximum'
            }),
            'image_url': TextInput(attrs={
                'class': 'form-control mb-2', 'placeholder': ' Optional'
            })
        }
        labels = {'title': '', 'category': '', 'min_bid': '', 'description': '', 'image_url': ''}
        help_texts = {'title': '', 'min_bid': '', 'description': ''}

class BidForm(ModelForm):
    class Meta:
        model = Bid
        fields = ['bid']
        widgets = {
            'bid': NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Bid here.'}
            )
        }

    def __init__(self, *args, **kwargs):
        """
        Constructor that looks for top_bid and min_bid
        values needed when validating new bid entered on this form.
        """
        if kwargs:
            self.top_bid = kwargs.pop('top_bid')
            self.min_bid = kwargs.pop('min_bid')
        super(BidForm, self).__init__(*args, **kwargs)

    def clean_bid(self):
        """
        Custom validator to make sure the bid entered
        is greater than or equal to the listings minimum bid and
        larger than the current top bid.
        """
        new_bid = int(self.cleaned_data['bid'])
        top_bid = int(self.top_bid)
        min_bid = int(self.min_bid)
        if new_bid == 0:
            raise forms.ValidationError(
                f"Bid cannot be $0."
            )
        if new_bid < top_bid or new_bid == top_bid:
            raise forms.ValidationError(
                "Bid has to be greater than the Current price.")

        if new_bid < min_bid:
            raise forms.ValidationError(
                "Bid has to be greater than or equal to the Starting price."
            )
        return new_bid

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['title', 'message']
        widgets = {
            'title': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Subject'}
            ),
            'message': Textarea(attrs={
                'class': 'form-control', 'rows': '6',
                'placeholder': 'Your Message'
            })
        }