#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging as log
import tempfile
from pathlib import Path
import ijson
from constance import config
from typing import Optional
import sys
import re
from apify_client import ApifyClient
from apify.log import ActorLogFormatter
from reunite.common.apify_temp_table import add_temp_record, ApifyFacebookPost
from reunite.models import FacebookPhoto, FacebookPost, Case
from storages.backends.s3boto3 import S3Boto3Storage
from .common_utils import download_file
import requests

log.basicConfig(format='[ %(levelname)s ] %(message)s', level=log.INFO, stream=sys.stdout)

handler = log.StreamHandler()
handler.setFormatter(ActorLogFormatter())

apify_client_logger = log.getLogger('apify_client')
apify_client_logger.setLevel(log.INFO)
apify_client_logger.addHandler(handler)

apify_logger = log.getLogger('apify')
apify_logger.setLevel(log.DEBUG)
apify_logger.addHandler(handler)


class ApifyFacebookScrapperImporter:
    def __init__(self):
        self.apify_posts = []
        self.posts_imported = 0
        self.photos_imported = 0
        self.cases_imported = 0
        self.storage = S3Boto3Storage()

    @staticmethod
    def find_code(text: str) -> Optional[str]:
        lines = text.split('\n')
        for line in lines:
            if any(map(line.__contains__, ['code', 'كود'])):
                cleaned = re.sub('[^0-9]', '', line)
                log.info(f'Found code line: {cleaned}')
                try:
                    cleaned = int(cleaned)
                    return str(cleaned)
                except ValueError:
                    log.warning(f'Error while finding code for: {cleaned}')
                    return None

    # Try real hard to see if we have a similar Facebook post
    def get_django_post(self, temp_post: ApifyFacebookPost) -> Optional[FacebookPost]:
        post = None
        if temp_post.post_id is not None and temp_post.post_id != '':
            post = FacebookPost.objects.filter(post_id=temp_post.post_id).first()
        if post is None:
            post = FacebookPost.objects.filter(post_url=temp_post.url).first()
        if post is None:
            post = FacebookPost.objects.filter(post_url=temp_post.top_level_url).first()

        if post is None:
            for temp_photo in temp_post.photos:
                for django_photo in FacebookPhoto.objects.all():
                    if django_photo.photo_file_name == temp_photo.photo_file_name():
                        post = django_photo.post
                        break
        return post

    def import_temp_records(self):
        from .apify_temp_table import session
        temp_posts = session.query(ApifyFacebookPost).all()
        for temp_post in temp_posts:
            django_post = self.get_django_post(temp_post)

            if django_post is not None:
                post = django_post
            else:
                post = FacebookPost()

            post.post_url = temp_post.url
            if temp_post.post_id is not None:
                post.post_id = temp_post.post_id
            if temp_post.text is not None and temp_post.text != "":
                post.post_text = temp_post.text

            post.post_time = temp_post.post_time
            post.case_code = self.find_code(temp_post.text)
            if temp_post.facebook_id is not None:
                post.facebook_id = temp_post.facebook_id
            post.save()

            self.posts_imported = self.posts_imported + 1
            if post.case_code is not None:
                case = Case.objects.filter(case_code=post.case_code).first()
                if case is None:
                    case = Case()
                    self.cases_imported = self.cases_imported + 1
                case.description = post.post_text
                case.case_code = post.case_code
                case.save()
                case.posts.add(post)
                case.save()

            django_photos = []

            for temp_photo in temp_post.photos:
                photo = FacebookPhoto.objects.filter(photo_image_url=temp_photo.photo_image_url).first()
                if photo is None:
                    photo = FacebookPhoto.objects.filter(media_id=temp_photo.media_id).first()
                if photo is None:
                    photo = FacebookPhoto()
                photo.url = temp_photo.url
                photo.ocr_text = temp_photo.ocr_text
                photo.photo_image_url = temp_photo.photo_image_url
                photo.media_id = temp_photo.media_id
                django_photos.append(photo)

            for photo in django_photos:
                try:
                    photo.post = post
                    photo.save()
                    self.photos_imported = self.photos_imported + 1
                    self.upload_photo(photo)
                except Exception as ex:
                    log.exception(ex)

    def upload_photo(self, photo: FacebookPhoto) -> None:
        file_name = photo.photo_file_name
        file_name_in_bucket = f'original/{file_name}'
        if not self.storage.exists(file_name_in_bucket):
            log.info(f'Photo {file_name_in_bucket} not in bucket. Uploading.')
            response = None
            for _ in range(3):
                try:
                    response = requests.get(photo.photo_image_url)
                    if response.status_code in [200, 404]:
                        break
                except requests.exceptions.ConnectionError:
                    pass

            if response is not None and response.status_code == 200:
                # Default ACL is private
                file = self.storage.open(file_name_in_bucket, 'w')
                file.write(response.content)
                file.close()
                log.info(f'Photo {file_name_in_bucket} not in bucket. Uploaded.')

    def import_page(self, url: str):
        # Initialize the ApifyClient with your API token
        client = ApifyClient(config.APIFY_API_KEY)

        # Prepare the Actor input
        run_input = {
            "startUrls": [{"url": url}],
            "resultsLimit": 100,
            "proxy": {
                "useApifyProxy": True,
                "apifyProxyGroups": ["RESIDENTIAL"],
            },
            "maxRequestRetries": 10,
        }
        # Run the Actor and wait for it to finish
        run = client.actor("apify/facebook-posts-scraper").call(run_input=run_input)

        # Fetch and print Actor results from the run's dataset (if there are any)
        for record in client.dataset(run["defaultDatasetId"]).iterate_items():
            add_temp_record(record)
        self.import_temp_records()

        print(f'Posts: {self.posts_imported}')
        print(f'Photos: {self.photos_imported}')
        print(f'Cases: {self.cases_imported}')

    def import_url(self, url: str):
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            temp_file_name = tmp_file.name
        download_file(url, Path(temp_file_name))
        with open(temp_file_name, "rb") as f:
            for record in ijson.items(f, "item"):
                add_temp_record(record)
        self.import_temp_records()

        print(f'Posts: {self.posts_imported}')
        print(f'Photos: {self.photos_imported}')
        print(f'Cases: {self.cases_imported}')


if __name__ == '__main__':
    ApifyFacebookScrapperImporter().import_page('https://www.facebook.com/atfalmafkoda')
