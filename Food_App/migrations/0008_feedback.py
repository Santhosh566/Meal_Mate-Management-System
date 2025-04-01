# Generated by Django 5.1.2 on 2025-02-06 22:08

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Food_App', '0007_favorite'),
    ]

    operations = [
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField(choices=[(1, '1 Star'), (2, '2 Stars'), (3, '3 Stars'), (4, '4 Stars'), (5, '5 Stars')], validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('comment', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('food_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Food_App.fooditem')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Food_App.order')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Food_App.registration')),
            ],
            options={
                'ordering': ['-created_at'],
                'unique_together': {('user', 'food_item', 'order')},
            },
        ),
    ]
