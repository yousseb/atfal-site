#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path
import requests


def download_file(url: str, path: Path) -> None:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.35 (KHTML, like Gecko) '
                      'Chrome/39.0.2171.95 Safari/537.36'}
    r = requests.get(url, headers=headers)
    with open(path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
    return
