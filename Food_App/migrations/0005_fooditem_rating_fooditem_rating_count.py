# Generated by Django 5.1.2 on 2025-02-04 05:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Food_App', '0004_order_payment_method_order_payment_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='fooditem',
            name='rating',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=3),
        ),
        migrations.AddField(
            model_name='fooditem',
            name='rating_count',
            field=models.IntegerField(default=0),
        ),
    ]
