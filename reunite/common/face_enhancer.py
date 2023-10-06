#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import logging as log
import tempfile
import urllib
from pathlib import Path
import ijson
from constance import config
from typing import Optional
import sys
import re
from reunite.models import FacebookPhoto, EnhancedFace
from storages.backends.s3boto3 import S3Boto3Storage
import requests
from .common_utils import download_file

log.basicConfig(format='[ %(levelname)s ] %(message)s', level=log.INFO, stream=sys.stdout)

headers = {'Content-Type': 'application/json',
           'Accept-Encoding': 'gzip, deflate',
           'Connection': 'close',
           'X-API-Key': config.AI_API_KEY}


class FaceEnhancer:
    def __init__(self):
        self.photos_processed = 0
        self.storage = S3Boto3Storage()

    def enhance_faceboxes(self, max_photos: int = -1):
        for facebook_photo in FacebookPhoto.objects.all():
            if facebook_photo.face_boxes is None or facebook_photo.face_boxes == '':
                pass
            else:
                face_boxes = json.loads(facebook_photo.face_boxes)
                photo_url = facebook_photo.preview_url()
                ai_endpoint = config.AI_SERVER_URL + 'enhance/'
                params = {'image_url': photo_url}

                for bb in face_boxes:
                    if not self.is_already_processed(facebook_photo, bb):
                        log.info(f'Processing face bounding box enhancement for facebook_photo: {facebook_photo.id} '
                                 f'and bounding box: {bb}')

                        response = requests.post(ai_endpoint, params=params, json=bb, headers=headers)
                        if response.status_code == 200:
                            log.info(f'Response: Received enhanced face')

                            enhanced_face = EnhancedFace()
                            file_name = str(enhanced_face.id) + '.png'
                            enhanced_face.file_name = file_name
                            enhanced_face.original_face_box = json.dumps(bb)
                            enhanced_face.facebook_photo = facebook_photo

                            file_name_in_bucket = f'enhanced/{file_name}'
                            log.info(f'Uploading to {file_name_in_bucket}')
                            if not self.storage.exists(file_name_in_bucket):
                                if response is not None and response.status_code == 200:
                                    # Default ACL is private
                                    file = self.storage.open(file_name_in_bucket, 'w')
                                    file.write(response.content)
                                    file.close()
                                    enhanced_face.save()

                        else:
                            log.error(f'Response code: {response.status_code}, Text:{response.text}')
                        self.photos_processed = self.photos_processed + 1

    def is_already_processed(self, facebook_photo: FacebookPhoto, bb: dict) -> bool:
        enhanced_faces = EnhancedFace.objects.filter(facebook_photo=facebook_photo)
        for enhanced_face in enhanced_faces:
            box = json.loads(enhanced_face.original_face_box)
            if bb['x1'] == box['x1'] and bb['x2'] == box['x2'] and bb['y1'] == box['y1'] and bb['y2'] == box['y2']:
                return True
        return False
