# Generated by Django 4.0 on 2022-03-26 16:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ui', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='filter',
            name='page_type',
        ),
    ]