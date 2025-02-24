# Generated by Django 4.2.18 on 2025-02-24 18:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_booking', '0019_alter_booking_billing_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='status',
            field=models.CharField(choices=[('pending', 'Függőben'), ('accepted', 'Elfogadva'), ('cancelled', 'Lemondva'), ('post_cancelled', 'Utólag Lemondva')], default='pending', max_length=20, verbose_name='Foglalás státusza'),
        ),
        migrations.AlterField(
            model_name='emailtemplate',
            name='type',
            field=models.CharField(choices=[('pending', 'Függőben lévő foglalás'), ('accepted', 'Elfogadott foglalás'), ('cancelled', 'Elutasított foglalás'), ('rejected_after_accepted', 'Utólag elutasított foglalás')], max_length=30, unique=True),
        ),
    ]
