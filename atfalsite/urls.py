"""
URL configuration for atfalsite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls.i18n import i18n_patterns
from django.shortcuts import redirect
from django.urls import include, path, re_path
from rest_framework.decorators import api_view
from reunite import views
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import routers

router = routers.DefaultRouter(trailing_slash=False)
router.register('case-list', views.CaseViewSet)

swagger_info = openapi.Info(
    title="Atfal-Site API",
    default_version='v1',
    description="""Atfal-mafkooda API.

""",  # noqa
    terms_of_service="",
    contact=openapi.Contact(email=""),
    license=openapi.License(name="MIT License"),
)

SchemaView = get_schema_view(
    swagger_info,
    validators=['ssv', 'flex'],
    public=True,
    permission_classes=[permissions.AllowAny],
)


@api_view(['GET'])
def plain_view(request):
    pass

urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),
    re_path('flower/(?P<path>.*)', views.flower_app, name='flower'),

    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    path('swagger<format>/', SchemaView.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', SchemaView.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
urlpatterns += i18n_patterns(path("admin/", admin.site.urls))


# https://medium.com/@dvianna/fine-tuning-bloomz-for-legal-question-answering-f964b5c0657f
