# Generated by Django 5.0.3 on 2024-05-01 21:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0010_alter_atrakcja_opis'),
    ]

    operations = [
        migrations.AlterField(
            model_name='atrakcja',
            name='opis',
            field=models.TextField(max_length=900),
        ),
    ]
