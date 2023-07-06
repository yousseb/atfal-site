from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse


class XAccelRedirectResponse(HttpResponse):
    def __init__(self, path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self['X-Accel-Redirect'] = '/protected' + path
        del self['Content-Type']  # necessary


# I chose to only allow staff members, i.e. whose who can access the admin panel
@staff_member_required
@csrf_exempt
def flower_app(request, path):
    query_str = request.META['QUERY_STRING']  # you must keep the query string
    return XAccelRedirectResponse(f'/flower/{path}?{query_str}')
