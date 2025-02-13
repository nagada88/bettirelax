# Generated by Django 4.2.18 on 2025-02-13 19:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_booking', '0010_bookingsettings_booking_puffer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookingsettings',
            name='booking_puffer',
            field=models.DecimalField(decimal_places=0, default=0, max_digits=3, verbose_name='puffer idő (percekben)'),
        ),
    ]
