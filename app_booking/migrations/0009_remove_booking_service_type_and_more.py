# Generated by Django 4.2.18 on 2025-02-11 17:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_booking', '0008_booking_service_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='booking',
            name='service_type',
        ),
        migrations.AlterField(
            model_name='booking',
            name='booked_service_type',
            field=models.TextField(default=''),
        ),
    ]
