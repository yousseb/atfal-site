#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Iterator, Optional
from facebook_scraper import FacebookScraper, Post
from types import SimpleNamespace
from facebook_scraper.utils import parse_cookie_file
import logging as log
import re
from pathlib import Path
from urllib.parse import urlparse, unquote
import json
import tempfile
import os


class FacebookUtility:
    def __init__(self):
        self.map = {}
        self.posts = {}

    def find_code(self, post: Post) -> Optional[str]:
        lines = post['text'].split('\n')
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

        log.warning(f'Post has no code: {post}')
        return None

    def build_index(self) -> Iterator[Post]:
        import facebook_scraper as fs
        fs.set_user_agent(
             'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36')

        gen = fs.get_posts(
            post_urls=['https://www.facebook.com/100064496780643/posts/662698879223332'],
            options={"comments": False,
                     "reactors": False,
                     "allow_extra_requests": True,
                     "progress": True}
        )

        while True:
            post = None
            try:
                post = next(gen)
                sn = SimpleNamespace(**post)
                print(sn)
                self.posts[sn.post_id] = post
            except StopIteration:
                break

            code = self.find_code(post)
            post_images = post['images']

            if code is None:
                code = "no-code"

            code_exists = False
            if code in self.map:
                code_exists = True
                log.info('Code was repeated - could be a repost')

            images = []
            for image in post_images:
                url_parsed = urlparse(image)
                cleaned_image = unquote(Path(url_parsed.path).name)
                # cleaned_image = cleaned_image.split("?")[0]
                images.append(cleaned_image)

            if code_exists:
                self.map[code] = self.map[code] + images
                self.map[code] = list(set(self.map[code]))  # Unique
            else:
                self.map[code] = images

        return gen


if __name__ == '__main__':
    FacebookUtility().build_index()
