# Generated by Django 4.2.13 on 2024-06-02 14:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('instagram_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='full_name',
            field=models.CharField(default='', max_length=100),
        ),
    ]
