# Generated by Django 4.0.3 on 2025-01-30 15:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_bettirelax', '0013_rename_adress_contact_address_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='contact',
            name='facebook_messenger',
            field=models.CharField(default='', max_length=150, verbose_name='facebook messenger'),
        ),
    ]
