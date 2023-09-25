#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.management import BaseCommand
from reunite.common.apify_facebook_scrapper_importer import ApifyFacebookScrapperImporter


class Command(BaseCommand):
    help = "Imports the full Atfal-mafkooda page from Apify runs"

    def handle(self, *args, **options):
        json_url = 'https://api.apify.com/v2/datasets/VXKqJ33pWoVJ7A8fb/items?clean=true&format=json'
        ApifyFacebookScrapperImporter().import_url(json_url)
