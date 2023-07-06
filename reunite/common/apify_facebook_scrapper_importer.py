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
from reunite.models import FacebookPhoto, FacebookPost, Case
from storages.backends.s3boto3 import S3Boto3Storage
import requests

storage = S3Boto3Storage()
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

    def download_file(self, url: str, path: Path):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.35 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        r = requests.get(url, headers=headers)
        with open(path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
        return

    # def download_posts(self, url: str):
    #     headers = {
    #         'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.35 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    #     r = requests.get(url, headers=headers)
    #     text = r.text
    #     self.apify_posts = json.loads(text, object_hook=lambda d: SimpleNamespace(**d))

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

    @staticmethod
    def post_is_share(post) -> bool:
        if hasattr(post, "text"):
            return False
        else:
            return True

    def import_record(self, record):
        post_id = record["postId"]

        if 'sharedPost' in record:
            log.warning(f'Post {post_id} has sharedPost. Will only import media from sharedPost, but not post or case.')
            media = record['sharedPost']['media']
            photos = []
            for media_item in media:
                if '__typename' in media_item:
                    media_typename = media_item['__typename']
                    if media_typename.lower() == 'photo' and 'photo_image' in media_item:     # Photo?
                        photo_image_uri = media_item['photo_image']['uri']
                        media_url = media_item['url']
                        ocr_text = media_item['ocrText']

                        try:
                            photo = FacebookPhoto.objects.get(media_id=media_item['id'])
                        except:
                            photo = FacebookPhoto()
                        photo.url = media_url
                        photo.ocr_text = ocr_text
                        photo.photo_image_url = photo_image_uri
                        photo.media_id = media_item['id']
                        photos.append(photo)
            for photo in photos:
                file_name = photo.photo_file_name()
                file_name_in_bucket = f'original/{file_name}'
                if not storage.exists(file_name_in_bucket):
                    log.info(f'Photo {file_name_in_bucket} not in bucket. Uploading.')
                    for _ in range(3):
                        try:
                            response = requests.get(photo.photo_image_url)
                            if response.status_code in [200, 404]:
                                break
                        except requests.exceptions.ConnectionError:
                            pass

                    if response is not None and response.status_code == 200:
                        # Default ACL is private
                        file = storage.open(file_name_in_bucket, 'w')
                        file.write(response.content)
                        file.close()
                        log.info(f'Photo {file_name_in_bucket} not in bucket. Uploaded')
            return

        if 'media' not in record or 'text' not in record:
            log.warning(f'Post {post_id} has no text and mo media. Likely a re-share of old post.')
            return False

        post_time = record["time"]
        post_timestamp = record["timestamp"]
        post_feedback_id = record["feedbackId"]
        post_top_level_url = record["topLevelUrl"]
        post_facebook_id = record["facebookId"]
        text = None
        media = None
        text = record['text']

        photos = []
        media = record['media']
        for media_item in media:
            if '__typename' in media_item:
                media_typename = media_item['__typename']  # Photo
                if media_typename.lower() == 'photo' and 'photo_image' in media_item:
                    photo_image_uri = media_item['photo_image']['uri']
                    media_url = media_item['url']
                    ocr_text = media_item['ocrText']

                    try:
                        photo = FacebookPhoto.objects.get(media_id=media_item['id'])
                    except:
                        photo = FacebookPhoto()
                    photo.url = media_url
                    photo.ocr_text = ocr_text
                    photo.photo_image_url = photo_image_uri
                    photo.media_id = media_item['id']
                    photos.append(photo)
                else:
                    log.warning(f"post {post_id}: Media is not a photo. Skipping")
            else:
                log.warning(f'Could not determine media type for post {post_id}. Skipping.')

        if len(photos) == 0:
            log.warning(f'Photos 0 for post {post_id}. Skipping.')
            return False

        try:
            post = FacebookPost.objects.get(post_id=post_id)
        except:
            post = FacebookPost()
        post.post_url = post_top_level_url
        post.post_id = post_id
        post.post_text = text
        post.post_time = post_time
        post.case_code = self.find_code(text)
        post.facebook_id = post_facebook_id
        post.save()
        self.posts_imported = self.posts_imported + 1
        if post.case_code is not None:
            try:
                case = Case.objects.get(case_code=post.case_code)
            except:
                case = Case()
                self.cases_imported = self.cases_imported + 1
            case.description = post.post_text
            case.case_code = post.case_code
            case.save()
            case.posts.add(post)
            case.save()

        for photo in photos:
            try:
                photo.post = post
                photo.save()
                self.photos_imported = self.photos_imported + 1

                file_name = photo.photo_file_name()
                file_name_in_bucket = f'original/{file_name}'
                if not storage.exists(file_name_in_bucket):
                    log.info(f'Photo {file_name_in_bucket} not in bucket. Uploading.')
                    for _ in range(3):
                        try:
                            response = requests.get(photo.photo_image_url)
                            if response.status_code in [200, 404]:
                                break
                        except requests.exceptions.ConnectionError:
                            pass

                    if response is not None and response.status_code == 200:
                        # Default ACL is private
                        file = storage.open(file_name_in_bucket, 'w')
                        file.write(response.content)
                        file.close()
                        log.info(f'Photo {file_name_in_bucket} not in bucket. Uploaded.')

            except Exception as ex:
                log.exception(ex)

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
            self.import_record(record)

        print(f'Posts: {self.posts_imported}')
        print(f'Photos: {self.photos_imported}')
        print(f'Cases: {self.cases_imported}')

    def import_url(self, url: str):
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            temp_file_name = tmp_file.name
        self.download_file(url, Path(temp_file_name))
        with open(temp_file_name, "rb") as f:
            for record in ijson.items(f, "item"):
                self.import_record(record)

        print(f'Posts: {self.posts_imported}')
        print(f'Photos: {self.photos_imported}')
        print(f'Cases: {self.cases_imported}')


if __name__ == '__main__':
    ApifyFacebookScrapperImporter().import_page('https://www.facebook.com/atfalmafkoda')
