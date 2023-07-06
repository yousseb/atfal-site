#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging as log
import sys
from django.core.management import BaseCommand
from apify.log import ActorLogFormatter
from reunite.common.apify_facebook_scrapper_importer import ApifyFacebookScrapperImporter


log.basicConfig(format='[ %(levelname)s ] %(message)s', level=log.DEBUG, stream=sys.stdout)

handler = log.StreamHandler()
handler.setFormatter(ActorLogFormatter())

apify_client_logger = log.getLogger('apify_client')
apify_client_logger.setLevel(log.INFO)
apify_client_logger.addHandler(handler)

apify_logger = log.getLogger('apify')
apify_logger.setLevel(log.DEBUG)
apify_logger.addHandler(handler)


class Command(BaseCommand):
    help = "Imports the full Atfal-mafkooda page"

    def handle(self, *args, **options):
        ApifyFacebookScrapperImporter().import_page('https://www.facebook.com/atfalmafkoda')

