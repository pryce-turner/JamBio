# Generated by Django 2.1.5 on 2019-01-08 22:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('QC', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='executionstats',
            name='website_order_id',
        ),
    ]
