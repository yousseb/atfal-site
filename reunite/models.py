import uuid
from django.db import models
from django.urls import reverse
from django.utils.html import format_html, escape
from django.utils.translation import gettext_lazy as _
from pathlib import Path
from urllib.parse import urlparse, unquote, urlsplit
from django.utils.safestring import mark_safe
from django.shortcuts import resolve_url
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from storages.backends.s3boto3 import S3Boto3Storage
storage = S3Boto3Storage()


class Case(models.Model):
    """
    Case - missing or found
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    case_code = models.CharField(max_length=200, unique=True,
                                 db_comment='Case Code', null=True, help_text=_('Case code'))
    description = models.TextField(db_comment='Facebook post text', null=True, help_text=_('Facebook post text'))

    class CaseStatus(models.IntegerChoices):
        UNKNOWN = 0, _('Unclassified')
        MISSING = 1, _('Missing')
        JOHN_DOE = 2, _('John Doe')
        REUNITED = 3, _('Reunited')
        DECEASED = 4, _('Deceased')

    case_status = models.IntegerField(
        choices=CaseStatus.choices,
        default=CaseStatus.UNKNOWN,
    )

    posts = models.ManyToManyField(
        'FacebookPost',
        through="CasePost",
        through_fields=("case", "post"),
    )

    def fb_posts(self):
        i = 1
        posts = []
        for post in self.posts.all():
            url = resolve_url(admin_urlname(FacebookPost._meta, 'change'), post.id)
            link = f'<a href="{url}"> <i class="fas fa-clipboard"></i> </a>'
            posts.append(link)
            i = i + 1
        return format_html(','.join(posts))
    fb_posts.short_description = 'Posts'

    @staticmethod
    def autocomplete_search_fields():
        return ("case_code__iexact", "description__icontains",)


class FacebookPost(models.Model):
    """
    Facebook post
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post_url = models.URLField(db_comment='Post URL', help_text=_('Facebook post URL'))
    post_id = models.CharField(max_length=200, unique=True, db_comment='Post id',
                               help_text=_('Facebook unique post id'))
    post_text = models.TextField(max_length=6000, db_comment='Post text', null=True, help_text=_('Facebook post text'))
    post_time = models.DateTimeField(db_comment='Post time', null=True, help_text=_('Facebook post time'))
    case_code = models.CharField(max_length=200, db_comment='Case Code', null=True, help_text=_('Case code from text'))
    facebook_id = models.CharField(max_length=200, unique=False, db_comment='Facebook post id', null=True,
                                   help_text=_('Importer Facebook post id'))

    # # Metadata
    class Meta:
        ordering = ['-case_code']

    # Methods
    def get_absolute_url(self):
        """Returns the URL to access a particular instance of MyModelName."""
        return reverse('model-detail-view', args=[str(self.id)])

    def __str__(self):
        """String for representing the MyModelName object (in Admin site etc.)."""
        return self.case_code or '(no case id)'


class CasePost(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    case = models.ForeignKey('Case', on_delete=models.CASCADE)
    post = models.ForeignKey('FacebookPost', on_delete=models.CASCADE)

    def post_preview(self):
        if self.post:
            text = self.post.post_text
            text = text.replace('\n', '<br/>')
            return format_html('<p dir="rtl" style="direction: rtl; text-align: right; word-break: break-all; white-space: normal;">{0}</p>'.format(text))
        else:
            return '(No post)'

    def __str__(self):
        return "{}_{}".format(self.case.__str__(), self.post.__str__())


class FacebookPhoto(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey('FacebookPost', on_delete=models.CASCADE)
    photo_image_url = models.URLField(max_length=1024,
                                      help_text=_('Facebook media image URL - NOTE: Will not work directly'))
    url = models.URLField(max_length=1024, help_text=_('Facebook photo URL'))
    media_id = models.CharField(max_length=200, unique=True, help_text=_('Facebook media id (unique)'))
    ocr_text = models.CharField(max_length=1024, db_comment='OCR Text', null=True, help_text=_('OCR Text'))

    # Methods
    def get_absolute_url(self):
        """Returns the URL to access a particular instance of MyModelName."""
        return reverse('model-detail-view', args=[str(self.id)])

    def photo_file_name(self):
        url_parsed = urlparse(self.photo_image_url)
        cleaned_image = unquote(Path(url_parsed.path).name)
        return format_html(cleaned_image)
        # cleaned_image = cleaned_image.split("?")[0]
    photo_file_name.short_description = _('File name')

    def preview_url(self):
        file_path_within_bucket = f'original/{self.photo_file_name()}'
        url = storage.url(file_path_within_bucket)
        return url

    def photo_preview(self):
        file_path_within_bucket = f'original/{self.photo_file_name()}'
        no_image_url = f'https://reunite-media.fra1.digitaloceanspaces.com/original/nophoto.jpg'
        #if storage.exists(file_path_within_bucket):
        url = storage.url(file_path_within_bucket)
        #print(url)
        # TODO: Put error image
        return format_html(f'<img onerror="this.src=\'{no_image_url}\'" src="{url}" />')
        #else:
        #    return '-'
    photo_preview.short_description = _('Photo')
    photo_preview.allow_tags = True

    def __str__(self):
        return "{}".format(self.media_id)
