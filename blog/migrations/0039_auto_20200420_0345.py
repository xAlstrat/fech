# Generated by Django 2.2.12 on 2020-04-20 03:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0038_ccee_pinned'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ccee',
            old_name='description',
            new_name='body',
        ),
    ]