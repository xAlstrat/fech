# Generated by Django 2.2.5 on 2019-10-02 20:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0015_auto_20191001_2034'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='formatted_address',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AddField(
            model_name='event',
            name='latlng_address',
            field=models.CharField(default='', max_length=255),
        ),
    ]
