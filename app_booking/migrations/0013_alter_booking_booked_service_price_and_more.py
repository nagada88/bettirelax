# Generated by Django 4.2.18 on 2025-02-13 19:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app_booking', '0012_booking_admin_token'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='booked_service_price',
            field=models.DecimalField(decimal_places=2, default=0, editable=False, max_digits=10, verbose_name='Szolgáltatás ára (Ft)'),
        ),
        migrations.AlterField(
            model_name='booking',
            name='booked_service_type',
            field=models.CharField(default='', max_length=30),
        ),
        migrations.AlterField(
            model_name='booking',
            name='user',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Foglaló'),
        ),
    ]
