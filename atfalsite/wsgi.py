"""
WSGI config for atfalsite project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
try:
    from psycopg2cffi import compat
    compat.register()
except:
    pass

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'atfalsite.settings')

application = get_wsgi_application()
