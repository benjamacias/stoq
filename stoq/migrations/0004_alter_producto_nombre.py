# Generated by Django 4.2.5 on 2024-03-21 17:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stoq', '0003_alter_producto_nombre'),
    ]

    operations = [
        migrations.AlterField(
            model_name='producto',
            name='nombre',
            field=models.CharField(max_length=200, unique=True),
        ),
    ]
