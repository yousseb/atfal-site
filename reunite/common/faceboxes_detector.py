#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging as log
import tempfile
import urllib
from pathlib import Path
import ijson
from constance import config
from typing import Optional
import sys
import re
from reunite.models import FacebookPhoto
from storages.backends.s3boto3 import S3Boto3Storage
import requests
from .common_utils import download_file

log.basicConfig(format='[ %(levelname)s ] %(message)s', level=log.INFO, stream=sys.stdout)

headers = {'Content-Type': 'application/json',
           'Accept-Encoding': 'gzip, deflate',
           'Connection': 'close',
           'X-API-Key': config.AI_API_KEY}


class FaceBoxesDetector:
    def __init__(self):
        self.photos_processed = 0
        self.storage = S3Boto3Storage()

    def detect_face_boxes(self, max_photos: int = -1):
        for facebook_photo in FacebookPhoto.objects.all():
            if facebook_photo.face_boxes is None or facebook_photo.face_boxes == '':
                photo_url = facebook_photo.preview_url()
                ai_endpoint = config.AI_SERVER_URL + 'faces/'
                params = {'image_url': photo_url}
                response = requests.get(ai_endpoint, params=params, headers=headers)
                if response.status_code == 200:
                    log.info(f'Response: {response.text}')
                    facebook_photo.face_boxes = response.text
                    facebook_photo.save()
                else:
                    log.error(f'Response code: {response.status_code}, Text:{response.text}')
                self.photos_processed = self.photos_processed + 1
