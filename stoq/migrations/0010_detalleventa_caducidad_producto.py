# Generated by Django 4.2.5 on 2024-04-09 15:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stoq', '0009_remove_venta_productos_venta_total_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='detalleventa',
            name='caducidad_producto',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='caduciad_producto', to='stoq.stock'),
            preserve_default=False,
        ),
    ]
