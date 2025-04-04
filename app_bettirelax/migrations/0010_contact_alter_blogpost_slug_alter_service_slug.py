# Generated by Django 4.0.3 on 2025-01-30 15:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_bettirelax', '0009_service_slug'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email_adress', models.CharField(default='', max_length=50, verbose_name='emailcím')),
                ('adress', models.CharField(default='', max_length=50, verbose_name='cím')),
                ('adress_link', models.CharField(default='', max_length=50, verbose_name='térkép link')),
                ('facebook', models.CharField(default='', max_length=150, verbose_name='facebook')),
                ('phone_number', models.CharField(default='', max_length=50, verbose_name='telefonszám')),
            ],
            options={
                'verbose_name': 'Kapcsolat',
                'verbose_name_plural': 'Kapcsolat',
            },
        ),
        migrations.AlterField(
            model_name='blogpost',
            name='slug',
            field=models.SlugField(blank=True, editable=False, max_length=200, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='service',
            name='slug',
            field=models.SlugField(blank=True, editable=False, unique=True),
        ),
    ]
