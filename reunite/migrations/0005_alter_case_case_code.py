# Generated by Django 4.2.1 on 2023-06-17 21:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reunite', '0004_alter_facebookphoto_media_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='case',
            name='case_code',
            field=models.CharField(db_comment='Case Code', help_text='Case code', max_length=200, null=True, unique=True),
        ),
    ]
