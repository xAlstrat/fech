# Generated by Django 2.2.9 on 2020-01-19 19:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0033_auto_20200118_0354'),
    ]

    operations = [
        migrations.AddField(
            model_name='content',
            name='pinned',
            field=models.BooleanField(default=False, verbose_name='Destacar'),
        ),
    ]
