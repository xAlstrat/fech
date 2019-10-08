# Generated by Django 2.2.5 on 2019-09-27 20:12

from django.db import migrations
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0007_blogpageauthor'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blogpageauthor',
            name='page',
            field=modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='authors', to='blog.BlogPage'),
        ),
    ]
