# Generated by Django 4.0.3 on 2025-01-30 23:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app_bettirelax', '0015_contact_contact_text'),
    ]

    operations = [
        migrations.AlterField(
            model_name='serviceprice',
            name='service',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prices', to='app_bettirelax.service'),
        ),
    ]
