# Generated by Django 4.2.18 on 2025-03-17 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_booking', '0023_bookingsettings_is_reviews_enabled'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='status',
            field=models.CharField(choices=[('pending', 'Függőben'), ('accepted', 'Elfogadva'), ('cancelled', 'Lemondva'), ('post_cancelled', 'Utólag Lemondva'), ('reminder', 'Foglalási emlékeztető')], default='pending', max_length=20, verbose_name='Foglalás státusza'),
        ),
    ]
