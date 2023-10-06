#!/usr/bin/env python
# -*- coding: utf-8 -*-

from celery import shared_task
from reunite.common.face_enhancer import FaceEnhancer


@shared_task
def face_enhancer_task():
    try:
        FaceEnhancer().enhance_faceboxes(max_photos=-1)
        return True
    except Exception as ex:
        raise ex
