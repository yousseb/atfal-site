#!/usr/bin/env python
# -*- coding: utf-8 -*-

from celery import shared_task
from reunite.common.faceboxes_detector import FaceBoxesDetector


@shared_task
def detect_faceboxes_task():
    try:
        FaceBoxesDetector().detect_face_boxes(max_photos=-1)
        return True
    except Exception as ex:
        raise ex
