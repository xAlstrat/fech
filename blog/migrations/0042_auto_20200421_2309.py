# Generated by Django 2.2.12 on 2020-04-21 23:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0041_auto_20200421_2202'),
    ]

    operations = [
        migrations.RenameField(
            model_name='archive',
            old_name='published_at',
            new_name='publish_at',
        ),
        migrations.RenameField(
            model_name='transparency',
            old_name='published_at',
            new_name='publish_at',
        ),
    ]
