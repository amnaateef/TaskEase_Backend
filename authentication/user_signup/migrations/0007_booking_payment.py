# Generated by Django 5.2.3 on 2025-07-07 13:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_signup', '0006_rename_category_service_selected_service_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='payment',
            field=models.CharField(choices=[('pending', 'Pending'), ('completed', 'Completed')], default='pending', max_length=20),
        ),
    ]
