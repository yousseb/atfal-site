#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re

from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'atfalsite.settings')

app = Celery('atfalsite')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

app.conf.task_routes = task_routes = ([
    ('reunite.tasks.apify_page_import_task.*', {'queue': 'feeds'}),  # Process facebook imports
    ('reunite.tasks.clear_tokens.*', {'queue': 'web'}),              # Web related
    ('reunite.tasks.detect_faceboxes_task.*', {'queue': 'ai'}),      # AI tasks
    (re.compile(r'(video|image)\.tasks\..*'), {'queue': 'media'}),   # Sample, unused
],)



# # Optional configuration, see the application user guide.
# app.conf.update(
#     result_expires=3600,
# )

if __name__ == '__main__':
    app.start()
