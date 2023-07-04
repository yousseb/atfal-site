# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# from typing import Iterator, Optional
# from facebook_scraper import FacebookScraper, Post
# from types import SimpleNamespace
# from facebook_scraper.utils import parse_cookie_file
# import logging as log
# import re
# from pathlib import Path
# from urllib.parse import urlparse, unquote
# import json
# import tempfile
# import os
#
#
# class FacebookUtility:
#     def __init__(self):
#         self.map = {}
#         self.posts = {}
#
#     def get_cookies(self) -> str:
#         cookies = '''# Netscape HTTP Cookie File
#             # http://curl.haxx.se/rfc/cookie_spec.html
#             # This is a generated file!  Do not edit.
#
#             .facebook.com	TRUE	/login/device-based/	TRUE	1716822758	dbln	%7B%22100091752205949%22%3A%22UZR7QIoC%22%7D
#             .facebook.com	TRUE	/	TRUE	1716822705	sb	cUpFZDWByc7U_ZsYpIYBF9WZ
#             .facebook.com	TRUE	/	TRUE	1682867549	wd	2327x1201
#             .facebook.com	TRUE	/	TRUE	1716822647	datr	cUpFZGGLRSEwkDc1a5Bdy60e
#             .facebook.com	TRUE	/	TRUE	1682867505	locale	en_US
#             .facebook.com	TRUE	/	TRUE	1713798700	c_user	100091752205949
#             .facebook.com	TRUE	/	TRUE	1713798700	xs	25%3AVRBLwBhOW7IQHw%3A2%3A1682262704%3A-1%3A-1
#             .facebook.com	TRUE	/	TRUE	1682867549	dpr	1.100000023841858
#             .facebook.com	TRUE	/	TRUE	1690038746	fr	0OmM4czJyZNkDQ4m3.AWUBolfSydV15jRIKekzF8_Hgk8.BkRUpx.y4.AAA.0.0.BkRUra.AWWgNVoab_E
#             .facebook.com	TRUE	/	TRUE	0	presence	C%7B%22t3%22%3A%5B%5D%2C%22utc3%22%3A1682262751568%2C%22v%22%3A1%7D
#             '''.lstrip().rstrip()
#         return cookies
#
#     def find_code(self, post: Post) -> Optional[str]:
#         lines = post['text'].split('\n')
#         for line in lines:
#             if any(map(line.__contains__, ['code', 'كود'])):
#                 log.info(f'Found code line: {line}')
#                 cleaned = re.sub('[^0-9]', '', line)
#                 try:
#                     cleaned = int(cleaned)
#                     return str(cleaned)
#                 except ValueError:
#                     log.warning(f'Error while finding code for: {cleaned}')
#                     return None
#
#         log.warning(f'Post has no code: {post}')
#         return None
#
#     def build_index(self) -> Iterator[Post]:
#         fs = FacebookScraper()
#         # fs.set_user_agent(
#         #     'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36')
#         fs.requests_kwargs['timeout'] = 120
#         username = 'sp8xi92lh7'
#         password = 't086msVRIloq4Yrwzl'
#         proxy = f'http://{username}:{password}@gate.smartproxy.com:7000'
#         fs.session.proxies.update({'http': proxy, 'https': proxy})
#         fs.set_proxy(proxy)
#
#         #tf = tempfile.NamedTemporaryFile(suffix='.txt', mode='w', delete=False)
#         #tf.write(self.get_cookies())
#         #tf.close()
#         #cookies = parse_cookie_file(tf.name)
#         #os.unlink(tf.name)
#         #fs.session.cookies.update(cookies)
#
#         # if not fs.is_logged_in():
#         #     raise RuntimeError('Cookies are not valid')
#
#         gen = fs.get_posts(
#             'atfalmafkoda',
#             pages=20,
#             options={"comments": False,
#                      "reactors": False,
#                      "allow_extra_requests": True,
#                      "progress": True}
#         )
#
#         while True:
#             post = None
#             try:
#                 post = next(gen)
#                 sn = SimpleNamespace(**post)
#                 print(sn)
#                 self.posts[sn.post_id] = post
#             except StopIteration:
#                 break
#
#             code = self.find_code(post)
#             post_images = post['images']
#
#             if code is None:
#                 code = "no-code"
#
#             code_exists = False
#             if code in self.map:
#                 code_exists = True
#                 log.info('Code was repeated - could be a repost')
#
#             images = []
#             for image in post_images:
#                 url_parsed = urlparse(image)
#                 cleaned_image = unquote(Path(url_parsed.path).name)
#                 # cleaned_image = cleaned_image.split("?")[0]
#                 images.append(cleaned_image)
#
#             if code_exists:
#                 self.map[code] = self.map[code] + images
#                 self.map[code] = list(set(self.map[code]))  # Unique
#             else:
#                 self.map[code] = images
#
#         # with open('map.json', 'w') as fp:
#         #     json.dump(self.map, fp, indent=2)
#         #
#         # with open('posts.json', 'w') as fp:
#         #     json.dump(self.posts, fp, indent=2)
#
#         return gen
#
#
# if __name__ == '__main__':
#     FacebookUtility().build_index()
