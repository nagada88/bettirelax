# Generated by Django 4.2.18 on 2025-02-08 21:54

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BookingSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_booking_enabled', models.BooleanField(default=True, verbose_name='Foglalási rendszer bekapcsolva?')),
                ('max_weeks_in_advance', models.PositiveIntegerField(choices=[(1, '1 hét'), (2, '2 hét'), (3, '3 hét'), (4, '4 hét'), (5, '5 hét'), (6, '6 hét'), (7, '7 hét'), (8, '8 hét'), (9, '9 hét'), (10, '10 hét'), (11, '11 hét'), (12, '12 hét')], default=4, verbose_name='Hány hétre előre lehet foglalni? (1-12)')),
                ('min_hours_before_booking', models.PositiveIntegerField(default=24, verbose_name='Legkésőbb mennyivel előre lehet foglalni? (órákban)')),
                ('auto_reject_time', models.PositiveIntegerField(default=12, verbose_name='Mennyi idő után utasítsuk el automatikusan? (órákban)')),
            ],
            options={
                'verbose_name': 'Foglalási beállítások',
                'verbose_name_plural': 'Foglalási beállítások',
            },
        ),
        migrations.CreateModel(
            name='SpecialOpeningHours',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(unique=True, verbose_name='Dátum')),
                ('start_time', models.TimeField(verbose_name='Nyitás')),
                ('end_time', models.TimeField(verbose_name='Zárás')),
            ],
            options={
                'verbose_name': 'Egyedi nyitvatartás',
                'verbose_name_plural': 'Egyedi nyitvatartások',
            },
        ),
        migrations.CreateModel(
            name='OpeningHours',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day_of_week', models.IntegerField(choices=[(0, 'Hétfő'), (1, 'Kedd'), (2, 'Szerda'), (3, 'Csütörtök'), (4, 'Péntek'), (5, 'Szombat'), (6, 'Vasárnap')], verbose_name='Nap')),
                ('is_even_week', models.BooleanField(default=True, verbose_name='Páros hét?')),
                ('start_time', models.TimeField(verbose_name='Nyitás')),
                ('end_time', models.TimeField(verbose_name='Zárás')),
            ],
            options={
                'verbose_name': 'Nyitvatartás',
                'verbose_name_plural': 'Nyitvatartások',
                'unique_together': {('day_of_week', 'is_even_week', 'start_time', 'end_time')},
            },
        ),
    ]
