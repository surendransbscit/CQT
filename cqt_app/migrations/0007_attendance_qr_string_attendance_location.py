# Generated by Django 5.1.1 on 2024-11-26 06:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cqt_app', '0006_holiday'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendance',
            name='QR_string',
            field=models.CharField(default='null', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='attendance',
            name='location',
            field=models.CharField(default='null', max_length=255),
            preserve_default=False,
        ),
    ]
