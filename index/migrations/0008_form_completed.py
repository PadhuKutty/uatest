# Generated by Django 5.0.6 on 2024-07-11 05:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0007_remove_form_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='form',
            name='completed',
            field=models.BooleanField(default=False),
        ),
    ]
