# Generated by Django 2.2.5 on 2019-10-01 20:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0013_benefit'),
    ]

    operations = [
        migrations.AddField(
            model_name='content',
            name='title',
            field=models.CharField(max_length=250, null=True, verbose_name='Título'),
        ),
    ]
