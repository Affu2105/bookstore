# Generated by Django 5.1.5 on 2025-04-03 06:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0002_book_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='image_url',
            field=models.URLField(blank=True, max_length=1000, null=True),
        ),
        migrations.AddField(
            model_name='book',
            name='s3_key',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
