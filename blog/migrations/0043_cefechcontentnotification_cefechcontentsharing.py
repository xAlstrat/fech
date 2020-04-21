# Generated by Django 2.2.12 on 2020-04-21 23:13

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0042_auto_20200421_2309'),
    ]

    operations = [
        migrations.CreateModel(
            name='CEFECHContentSharing',
            fields=[
                ('sharing_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='blog.Sharing')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('event', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='sharings', to='blog.CEFECHContent')),
            ],
            options={
                'ordering': ['-created_at'],
            },
            bases=('blog.sharing', models.Model),
        ),
        migrations.CreateModel(
            name='CEFECHContentNotification',
            fields=[
                ('notification_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='blog.Notification')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('new', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='blog.CEFECHContent')),
            ],
            options={
                'ordering': ['-created_at'],
            },
            bases=('blog.notification', models.Model),
        ),
    ]
