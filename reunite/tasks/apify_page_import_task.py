#!/usr/bin/env python
# -*- coding: utf-8 -*-

from celery import shared_task
from reunite.common.apify_page_importer import ApifyPageImporter


@shared_task
def import_page_task():
    try:
        ApifyPageImporter().import_page('https://www.facebook.com/atfalmafkoda')
        return True
    except:
        return False
