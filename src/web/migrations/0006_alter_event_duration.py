# Generated by Django 5.0.1 on 2024-03-22 19:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0005_event_external_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='duration',
            field=models.DurationField(blank=True, help_text='planned duration of this event', null=True),
        ),
    ]
