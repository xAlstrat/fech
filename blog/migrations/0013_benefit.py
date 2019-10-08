# Generated by Django 2.2.5 on 2019-10-01 19:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0012_auto_20191001_1946'),
    ]

    operations = [
        migrations.CreateModel(
            name='Benefit',
            fields=[
                ('content_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='blog.Content')),
                ('start', models.DateField(blank=True, null=True, verbose_name='Fecha de inicio')),
                ('end', models.DateField(blank=True, null=True, verbose_name='Fecha de término')),
            ],
            options={
                'abstract': False,
            },
            bases=('blog.content',),
        ),
    ]
