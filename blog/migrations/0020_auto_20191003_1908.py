# Generated by Django 2.2.6 on 2019-10-03 19:08

import datetime
from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0019_notification'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notification',
            name='content_type',
        ),
        migrations.RemoveField(
            model_name='notification',
            name='object_id',
        ),
        migrations.AddField(
            model_name='notification',
            name='channel',
            field=models.CharField(choices=[('EMAIL', 'EMAIL'), ('MOBILE', 'MOBILE')], default='EMAIL', max_length=16),
        ),
        migrations.AddField(
            model_name='notification',
            name='notified',
            field=models.BooleanField(default=False, verbose_name='Se ha notificado'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='notify_at',
            field=models.DateTimeField(default=datetime.datetime(2019, 10, 3, 19, 8, 20, 381199), verbose_name='Fecha de notificación'),
        ),
        migrations.CreateModel(
            name='EventNotification',
            fields=[
                ('notification_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='blog.Notification')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('event', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='blog.Event')),
            ],
            options={
                'abstract': False,
            },
            bases=('blog.notification', models.Model),
        ),
    ]
