# Generated by Django 4.2.2 on 2023-07-04 00:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reunite', '0011_alter_facebookphoto_photo_image_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='case',
            name='case_status',
            field=models.IntegerField(choices=[(0, 'Unclassified'), (1, 'Missing'), (2, 'John Doe'), (3, 'Reunited'), (4, 'Deceased')], default=0),
        ),
    ]
