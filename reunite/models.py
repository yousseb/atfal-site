import uuid

from cache_memoize import cache_memoize
from django.db import models
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.html import format_html, escape
from django.utils.translation import gettext_lazy as _
from pathlib import Path
from urllib.parse import urlparse, unquote, urlsplit
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

    def posts_description(self):
        posts = []
        for post in self.posts.all():
            post_text = post.post_text.replace('\n', '<br/>')
            photos = FacebookPhoto.objects.filter(post=post)
            photos_list = ""
            for photo in photos:
                photos_list = photos_list + ' ' + photo.photo_preview()
            photo_html = '<div style="margin: auto; width: 50%;">' + photos_list + '</div><br/>'
            post_text = photo_html + ('<div style="width: 100%; direction: rtl; '
                                      'text-align: right; white-space: normal;">') + post_text + '</div>'
            posts.append(post_text)
        joined = '<hr/>'.join(posts)
        return format_html(f'{joined}')

    posts_description.short_description = 'Description'

    @staticmethod
    def autocomplete_search_fields():
        return ("case_code__iexact", "description__icontains",)


class FacebookPost(models.Model):
    """
    Facebook post
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post_url = models.URLField(db_comment='Post URL', help_text=_('Facebook post URL'))
    post_id = models.CharField(max_length=200, unique=True, null=True, db_comment='Post id',
                               help_text=_('Facebook unique post id'))
    post_text = models.TextField(max_length=10000, db_comment='Post text', null=True, help_text=_('Facebook post text'))
    post_time = models.DateTimeField(db_comment='Post time', null=True, help_text=_('Facebook post time'))
    post_timestamp = models.BigIntegerField(db_comment='Post timestamp', null=True,
                                            help_text=_('Facebook post timestamp'))
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

    @cached_property
    def post_preview(self):
        if self.post:
            text = self.post.post_text
            text = text.replace('\n', '<br/>')
            return format_html(
                '<p style="direction: rtl; text-align: right; white-space: normal;">{0}</p>'.format(text))
        else:
            return '(No post)'

    def __str__(self):
        return "{}_{}".format(self.case.__str__(), self.post.__str__())


@cache_memoize(10000)
def get_signed_url(bucket_path):
    return storage.url(bucket_path, expire=10800)


class FacebookPhoto(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey('FacebookPost', on_delete=models.CASCADE)
    photo_image_url = models.URLField(max_length=1024,
                                      help_text=_('Facebook media image URL - NOTE: Will not work directly'))
    url = models.URLField(max_length=1024, help_text=_('Facebook photo URL'))
    media_id = models.CharField(max_length=200, null=True, help_text=_('Facebook media id (unique)'))
    ocr_text = models.CharField(max_length=1024, db_comment='OCR Text', null=True, help_text=_('OCR Text'))

    # Methods
    def get_absolute_url(self):
        """Returns the URL to access a particular instance of MyModelName."""
        return reverse('model-detail-view', args=[str(self.id)])

    @cached_property
    def photo_file_name(self):
        url_parsed = urlparse(self.photo_image_url)
        cleaned_image = unquote(Path(url_parsed.path).name)
        return format_html(cleaned_image)
        # cleaned_image = cleaned_image.split("?")[0]

    photo_file_name.short_description = _('File name')

    def preview_url(self):
        file_path_within_bucket = f'original/{self.photo_file_name}'
        url = get_signed_url(file_path_within_bucket)
        return url

    def photo_preview(self):
        file_path_within_bucket = f'original/{self.photo_file_name}'
        no_image_url = f'https://reunite-media.fra1.digitaloceanspaces.com/original/nophoto.jpg'
        url = get_signed_url(file_path_within_bucket)
        return format_html(f'<img onerror="this.src=\'{no_image_url}\'" '
                           f'src="{url}" '
                           f'style="max-width: 100%;height: auto;" />')

    photo_preview.short_description = _('Photo')
    photo_preview.allow_tags = True

    def __str__(self):
        return "{}".format(self.media_id)
