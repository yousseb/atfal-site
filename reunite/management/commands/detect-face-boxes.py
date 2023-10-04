#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.management import BaseCommand
from reunite.common.faceboxes_detector import FaceBoxesDetector


class Command(BaseCommand):
    help = "Generate Face Cuts using AI backend"

    def handle(self, *args, **options):
        FaceBoxesDetector().detect_face_boxes(max_photos=-1)
