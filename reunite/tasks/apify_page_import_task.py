#!/usr/bin/env python
# -*- coding: utf-8 -*-

from celery import shared_task
from reunite.common.apify_facebook_scrapper_importer import ApifyFacebookScrapperImporter


@shared_task
def import_page_task():
    try:
        ApifyFacebookScrapperImporter().import_page('https://www.facebook.com/atfalmafkoda')
        return True
    except:
        return False
