# Generated by Django 3.2.25 on 2024-06-10 20:00

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_alter_resourceinfo_info_memo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resourceinfo',
            name='info_memo',
            field=models.TextField(default=datetime.datetime(2024, 6, 11, 5, 0, 43, 293157)),
        ),
    ]
