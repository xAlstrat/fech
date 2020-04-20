# Generated by Django 2.2.12 on 2020-04-20 02:39

from django.db import migrations, models
import django.db.models.deletion
import wagtail.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailimages', '0001_squashed_0021'),
        ('blog', '0036_auto_20200414_0138'),
    ]

    operations = [
        migrations.CreateModel(
            name='CCEE',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now_add=True)),
                ('title', models.CharField(max_length=250, verbose_name='Título')),
                ('description', wagtail.core.fields.RichTextField(blank=True, verbose_name='Descripción')),
                ('address', models.CharField(blank=True, max_length=256, verbose_name='Dirección')),
                ('published', models.BooleanField(default=True, verbose_name='Publicado')),
                ('image', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='wagtailimages.Image', verbose_name='Imagen')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
