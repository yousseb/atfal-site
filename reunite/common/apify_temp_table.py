#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
from pathlib import Path
from typing import List
from urllib.parse import urlparse, unquote

import sqlalchemy
from sqlalchemy import create_engine, ForeignKey, BigInteger, DateTime
from sqlalchemy import Column, Date, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, relationship, mapped_column
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import dateutil
import logging as log


Session = sessionmaker()
Base = declarative_base()
engine = sqlalchemy.create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)


class ApifyFacebookPost(Base):
    __tablename__ = 'ApifyFacebookPost'
    __table_args__ = {'sqlite_autoincrement': True}

    id: Mapped[int] = mapped_column(primary_key=True, unique=True, index=True)
    post_id = Column(String(512), nullable=True)
    page_name = Column(String(512), nullable=False)
    post_time = Column(String(512), nullable=False)
    post_timestamp = Column(BigInteger, nullable=False)
    url = Column(String(1024), nullable=False, index=True)
    text = Column(String(10000), nullable=False)
    top_level_url = Column(String(1024), nullable=True, index=True)
    facebook_id = Column(String(512), nullable=True)
    is_share = Column(Boolean, nullable=False)

    photos: Mapped[List["ApifyFacebookPhoto"]] = relationship(back_populates="post")


class ApifyFacebookPhoto(Base):
    __tablename__ = 'ApifyFacebookPhoto'
    __table_args__ = {'sqlite_autoincrement': True}

    id: Mapped[int] = mapped_column(primary_key=True)
    photo_image_url = Column(String(1024), nullable=False, index=True)
    url = Column(String(1024), nullable=False, index=True)
    media_id = Column(String(1024), nullable=True, index=True)
    ocr_text = Column(String(1024), nullable=False, index=True)

    post_id: Mapped[int] = mapped_column(ForeignKey("ApifyFacebookPost.id"))
    post: Mapped["ApifyFacebookPost"] = relationship(back_populates="photos")

    def photo_file_name(self):
        url_parsed = urlparse(self.photo_image_url)
        cleaned_image = unquote(Path(url_parsed.path).name)
        return cleaned_image


Session.configure(bind=engine)
Base.metadata.create_all(engine)
session = Session()


def add_temp_record(record):
    shared = False
    if 'sharedPost' in record:
        shared = True

    if shared:
        record = record['sharedPost']

    post_time = record["time"]
    post_timestamp = record["timestamp"]
    post_url = record["url"]
    post_text = record["text"]

    if not shared:
        post_id = record["postId"]
        post_top_level_url = record["topLevelUrl"]
        post_facebook_id = record["facebookId"]

        post = ApifyFacebookPost(
            post_id=post_id,
            page_name='atfalmafkoda',
            post_time=post_time,
            post_timestamp=post_timestamp,
            url=post_url,
            text=post_text,
            top_level_url=post_top_level_url,
            facebook_id=post_facebook_id,
            is_share=shared
        )
    else:
        post = ApifyFacebookPost(
            page_name='atfalmafkoda',
            post_time=post_time,
            post_timestamp=post_timestamp,
            url=post_url,
            text=post_text,
            is_share=shared
        )

    media = record['media']
    for media_item in media:
        if '__typename' in media_item:
            media_typename = media_item['__typename']  # Photo
            if media_typename.lower() == 'photo' and 'photo_image' in media_item:
                photo_image_uri = media_item['photo_image']['uri']
                media_url = media_item['url']
                ocr_text = media_item['ocrText']

                photo = ApifyFacebookPhoto(
                    url=media_url,
                    ocr_text=ocr_text,
                    photo_image_url=photo_image_uri,
                    media_id=media_item['id'],
                )
                post.photos.append(photo)
            else:
                log.warning(f"post {post_url}: Media is not a photo. Skipping")
        else:
            log.warning(f'Could not determine media type for post {post_url}. Skipping.')

    session.add(post)
    session.commit()
