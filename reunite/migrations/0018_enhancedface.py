# Generated by Django 4.2.5 on 2023-10-05 19:20

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('reunite', '0017_facebookphoto_face_boxes'),
    ]

    operations = [
        migrations.CreateModel(
            name='EnhancedFace',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('original_face_box', models.CharField(db_comment='Face bounding box in original photo', help_text='Face bounding box in original photo', max_length=200, null=True)),
                ('ignore_in_search', models.BooleanField(db_comment='Ignore this enhanced face when doing searched', default=False, help_text='Ignore this enhanced face when doing searched.')),
                ('file_name', models.CharField(db_comment='File name in bucket', help_text='File name in bucket', max_length=200, null=True)),
                ('facebook_photo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reunite.facebookphoto')),
            ],
        ),
    ]
