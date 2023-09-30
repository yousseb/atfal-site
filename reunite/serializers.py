from collections import OrderedDict

from django.utils import timezone
from rest_framework import serializers
#from rest_framework_recursive.fields import RecursiveField

from .models import Case, FacebookPost


class CaseSerializer(serializers.ModelSerializer):
    posts = serializers.SlugRelatedField(many=True, read_only=True, slug_field='post_text')
    case_status = serializers.CharField(source='get_case_status_display')

    class Meta:
        model = Case
        fields = [
          'case_status',
          'posts'
        ]


class FacebookPostSerializer(serializers.ModelSerializer):
    class Meta:
        ordering = ['-id']
        model = FacebookPost
        fields = "_all__"
        extra_kwargs = {'post_id': {'required': False}}
