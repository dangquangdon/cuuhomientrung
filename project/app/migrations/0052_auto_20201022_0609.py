# Generated by Django 3.1.2 on 2020-10-21 23:09

from django.db import migrations
import mapbox_location_field.models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0051_auto_20201022_0553'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hodan',
            name='location',
            field=mapbox_location_field.models.LocationField(blank=True, map_attrs={}, null=True),
        ),
    ]