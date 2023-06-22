# Generated by Django 4.2.1 on 2023-06-19 03:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reunite', '0010_alter_facebookphoto_media_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='facebookphoto',
            name='photo_image_url',
            field=models.URLField(help_text='Facebook media image URL - NOTE: Will not work directly', max_length=1024),
        ),
    ]
