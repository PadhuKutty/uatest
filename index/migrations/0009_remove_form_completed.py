# Generated by Django 5.0.6 on 2024-07-11 05:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0008_form_completed'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='form',
            name='completed',
        ),
    ]
