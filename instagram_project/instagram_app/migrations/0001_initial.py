# Generated by Django 4.2.13 on 2024-05-16 08:49

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=100)),
                ('text', models.TextField()),
                ('created_at', models.DateTimeField()),
                ('post_link', models.URLField()),
            ],
        ),
    ]