# Generated by Django 4.2.18 on 2025-02-07 10:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app_bettirelax', '0019_bookingsettings_specialopeninghours_openinghours'),
    ]

    operations = [
        migrations.DeleteModel(
            name='BookingSettings',
        ),
        migrations.DeleteModel(
            name='OpeningHours',
        ),
        migrations.DeleteModel(
            name='SpecialOpeningHours',
        ),
    ]
