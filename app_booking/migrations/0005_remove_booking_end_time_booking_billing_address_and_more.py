# Generated by Django 4.2.18 on 2025-02-09 21:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app_bettirelax', '0021_bookingsettings_specialopeninghours_openinghours'),
        ('app_booking', '0004_remove_booking_day_of_week_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='booking',
            name='end_time',
        ),
        migrations.AddField(
            model_name='booking',
            name='billing_address',
            field=models.TextField(default='', verbose_name='Számlázási cím'),
        ),
        migrations.AddField(
            model_name='booking',
            name='billing_email',
            field=models.EmailField(default='', max_length=254, verbose_name='Számlázási email'),
        ),
        migrations.AddField(
            model_name='booking',
            name='billing_name',
            field=models.CharField(default='', max_length=255, verbose_name='Számlázási név'),
        ),
        migrations.AddField(
            model_name='booking',
            name='booked_service_length',
            field=models.PositiveIntegerField(default=30, verbose_name='Szolgáltatás időtartama (perc)'),
        ),
        migrations.AddField(
            model_name='booking',
            name='booked_service_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Szolgáltatás ára (Ft)'),
        ),
        migrations.AddField(
            model_name='booking',
            name='booked_service_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='app_bettirelax.service', verbose_name='Foglalt szolgáltatás'),
        ),
        migrations.AddField(
            model_name='booking',
            name='customer_email',
            field=models.EmailField(default='', max_length=254, verbose_name='Foglaló email címe'),
        ),
        migrations.AddField(
            model_name='booking',
            name='customer_name',
            field=models.CharField(default='', max_length=255, verbose_name='Foglaló neve'),
        ),
        migrations.AlterField(
            model_name='booking',
            name='date',
            field=models.DateField(null=True, verbose_name='Dátum'),
        ),
        migrations.AlterField(
            model_name='booking',
            name='start_time',
            field=models.TimeField(verbose_name='Kezdés'),
        ),
    ]
