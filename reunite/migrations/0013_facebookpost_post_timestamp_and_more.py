# Generated by Django 4.2.2 on 2023-09-24 16:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reunite', '0012_alter_case_case_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='facebookpost',
            name='post_timestamp',
            field=models.BigIntegerField(db_comment='Post timestamp', help_text='Facebook post timestamp', null=True),
        ),
        migrations.AlterField(
            model_name='facebookpost',
            name='post_text',
            field=models.TextField(db_comment='Post text', help_text='Facebook post text', max_length=10000, null=True),
        ),
    ]
