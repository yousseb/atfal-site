#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.management import BaseCommand
from reunite.common.face_enhancer import FaceEnhancer


class Command(BaseCommand):
    help = "Enhance face boxes AI backend"

    def handle(self, *args, **options):
        FaceEnhancer().enhance_faceboxes(max_photos=-1)
