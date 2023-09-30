from django.shortcuts import render, redirect
from rest_framework.permissions import IsAuthenticated

from ..models import Case
from ..serializers import CaseSerializer
from rest_framework import viewsets


# Create your views here.
class CaseViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Case.objects.all()
    serializer_class = CaseSerializer
