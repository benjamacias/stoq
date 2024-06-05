# Generated by Django 4.2.5 on 2024-04-09 15:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stoq', '0010_detalleventa_caducidad_producto'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='detalleventa',
            name='caducidad_producto',
        ),
        migrations.AddField(
            model_name='detalleventa',
            name='fecha_caducidad',
            field=models.DateField(blank=True, null=True),
        ),
    ]
