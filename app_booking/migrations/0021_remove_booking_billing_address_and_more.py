# Generated by Django 4.2.18 on 2025-02-24 18:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app_booking', '0020_alter_booking_status_alter_emailtemplate_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='booking',
            name='billing_address',
        ),
        migrations.RemoveField(
            model_name='booking',
            name='billing_city',
        ),
        migrations.RemoveField(
            model_name='booking',
            name='billing_email',
        ),
        migrations.RemoveField(
            model_name='booking',
            name='billing_name',
        ),
        migrations.RemoveField(
            model_name='booking',
            name='billing_tax_number',
        ),
        migrations.RemoveField(
            model_name='booking',
            name='billing_zip',
        ),
    ]
