# Generated by Django 4.1.7 on 2024-02-07 21:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='amsuser',
            name='is_pool_admin',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='amsuser',
            name='is_pool_user',
            field=models.BooleanField(default=False),
        ),
    ]
