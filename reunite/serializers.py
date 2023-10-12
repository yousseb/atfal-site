from collections import OrderedDict

from django.utils import timezone
from rest_framework import serializers
# from rest_framework_recursive.fields import RecursiveField

from .models import Case, FacebookPost, FacebookPhoto, EnhancedFace


class EnhancedFaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnhancedFace
        fields = ['id',
                  'original_face_box',
                  'ignore_in_search',
                  'signed_url']


class FacebookPhotoSerializer(serializers.ModelSerializer):
    enhanced_faces = EnhancedFaceSerializer(source='get_enhanced_faces', many=True)

    class Meta:
        model = FacebookPhoto
        fields = [
            'id',
            'ocr_text',
            'face_boxes',
            'preview_url',
            'enhanced_faces'
        ]


class FacebookPostSerializer(serializers.ModelSerializer):
    photos = FacebookPhotoSerializer(source='get_photos', many=True)

    class Meta:
        ordering = ['-id']
        model = FacebookPost
        fields = ['id',
                  'post_url',
                  'post_text',
                  'post_time',
                  'photos']
        extra_kwargs = {'post_id': {'required': False}}

    # def get_photos(self, obj):
    #     return FacebookPhotoSerializer(obj.get_photos())


class CaseSerializer(serializers.ModelSerializer):
    posts = FacebookPostSerializer(many=True, read_only=True)
    case_status = serializers.CharField(source='get_case_status_display')

    class Meta:
        model = Case
        fields = [
            'id',
            'case_code',
            'case_status',
            'posts'
        ]
