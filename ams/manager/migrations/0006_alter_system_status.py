# Generated by Django 4.1.7 on 2024-01-15 16:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0005_alter_system_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='system',
            name='status',
            field=models.CharField(default=None, max_length=256, null=True),
        ),
    ]
