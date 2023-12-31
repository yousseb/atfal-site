# Generated by Django 4.2.1 on 2023-06-17 22:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reunite', '0005_alter_case_case_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='facebookpost',
            name='facebook_id',
            field=models.CharField(db_comment='Facebook post id', help_text='Importer Facebook post id', max_length=200, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='facebookpost',
            name='post_id',
            field=models.CharField(db_comment='Post id', help_text='Facebook unique post id', max_length=200),
        ),
    ]
