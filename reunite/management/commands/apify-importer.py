#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path
import requests
import json
import logging as log
from types import SimpleNamespace
from typing import Iterator, Optional
import sys
import re
from argparse import ArgumentParser, SUPPRESS
import ijson
from django.core.management import BaseCommand

from reunite.models import FacebookPhoto, FacebookPost, Case


# log.basicConfig(format='[ %(levelname)s ] %(message)s', level=log.INFO, stream=sys.stdout)


class ApifyImporter:
    def __init__(self):
        self.apify_posts = []

    def download_file(self, url: str, path: Path):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.35 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        r = requests.get(url, headers=headers)
        with open(path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
        return

    def download_posts(self, url: str):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.35 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        r = requests.get(url, headers=headers)
        text = r.text
        self.apify_posts = json.loads(text, object_hook=lambda d: SimpleNamespace(**d))

    @staticmethod
    def find_code(text: str) -> Optional[str]:
        lines = text.split('\n')
        for line in lines:
            if any(map(line.__contains__, ['code', 'كود'])):
                log.info(f'Found code line: {line}')
                cleaned = re.sub('[^0-9]', '', line)
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

    def update_db_from_json(self, json_path: Path):
        posts_imported = 0
        photos_imported = 0
        cases_imported = 0

        with open(json_path, "rb") as f:
            for record in ijson.items(f, "item"):
                post_id = record["postId"]

                if 'media' not in record or 'text' not in record:
                    log.warning(f'Post {post_id} has no text and mo media. Likely a re-share of old post.')
                    continue

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
                        if media_typename.lower() == 'photo':
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
                    continue

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
                posts_imported = posts_imported + 1
                if post.case_code is not None:
                    try:
                        case = Case.objects.get(case_code=post.case_code)
                    except:
                        case = Case()
                        cases_imported = cases_imported + 1
                    case.description = post.post_text
                    case.case_code = post.case_code
                    case.save()
                    case.posts.add(post)
                    case.save()

                for photo in photos:
                    try:
                        photo.post = post
                        photo.save()
                        photos_imported = photos_imported + 1
                    except Exception as ex:
                        log.exception(ex)

        print(f'Posts: {posts_imported}')
        print(f'Photos: {photos_imported}')
        print(f'Cases: {cases_imported}')

    def import_url(self, url: str):
        # self.download_file(url, Path('apify_posts.json'))
        self.update_db_from_json(Path('apify_posts.json'))
        for post in self.apify_posts:
            if not self.post_is_share(post):
                log.info("Post: " + post.text)


class Command(BaseCommand):
    help = "Imports the full Atfal-mafkooda page"

    def handle(self, *args, **options):
        json_url = 'https://api.apify.com/v2/datasets/8CZdc4cMDDG02psKU/items?clean=true&format=json'
        ApifyImporter().import_url(json_url)


if __name__ == '__main__':
    json_url = 'https://api.apify.com/v2/datasets/8CZdc4cMDDG02psKU/items?clean=true&format=json'
    ApifyImporter().import_url(json_url)
