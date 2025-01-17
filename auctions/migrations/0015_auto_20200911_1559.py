# Generated by Django 3.1 on 2020-09-11 16:59

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0014_auto_20200714_1238'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='category',
            field=models.CharField(choices=[('M', 'Electronics & Games'), ('S', 'Sport & Recreation'), ('C', 'clothing & Accessories'), ('H', 'Home & Garden'), ('V', 'Cars & Trucks'), ('P', 'pets & Accessories'), ('A', 'antiques & Rare')], default='M', max_length=1),
        ),
        migrations.AlterField(
            model_name='listing',
            name='description',
            field=models.TextField(max_length=1000),
        ),
        migrations.AlterField(
            model_name='listing',
            name='min_bid',
            field=models.DecimalField(decimal_places=0, default=0, max_digits=7, validators=[django.core.validators.MinValueValidator(1, message='Bid must be $1 or greater')]),
        ),
        migrations.AlterField(
            model_name='user',
            name='first_name',
            field=models.CharField(blank=True, max_length=150, verbose_name='first name'),
        ),
    ]
