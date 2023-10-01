from django.shortcuts import render, redirect
from ..models import Case
from ..serializers import CaseSerializer
from rest_framework import permissions, viewsets


# Create your views here.
class CaseViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Case.objects.all()
    serializer_class = CaseSerializer
