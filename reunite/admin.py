from django.contrib import admin
from django import forms
from django.db import models
from django.utils.safestring import mark_safe
from import_export.admin import ImportExportModelAdmin
from related_admin import RelatedFieldAdmin

from .models import Case, FacebookPost, FacebookPhoto, CasePost
from django.utils.translation import gettext_lazy as _

# Admin site customization
admin.site.site_header = 'Reunite Administration'


# ---------------------  Model Registration

# ---------------------  Case
class CaseAdminForm(forms.ModelForm):
    class Meta:
        model = Case
        fields = ['case_code', 'case_status', 'posts']
        widgets = {'description': forms.Textarea(attrs={'dir': 'rtl', 'readonly': 'readonly'})}


class FacebookPostInlineAdmin(admin.TabularInline):
    model = Case.posts.through
    extra = 0
    verbose_name = _('Facebook Post')
    verbose_name_plural = _('Facebook Posts')
    fields = ['post', 'case', 'post_preview']
    readonly_fields = ['post_preview', ]


@admin.register(Case)
class CaseAdmin(ImportExportModelAdmin, RelatedFieldAdmin):
    form = CaseAdminForm
    model = Case

    list_display = ['case_code', 'fb_posts', 'posts_description', 'case_status']
    list_editable = ['case_status']
    list_filter = ['case_status']
    search_fields = ['case_code', 'description']
    verbose_name = _('Case')
    verbose_name_plural = _('Cases')
    list_per_page = 20
    # change_list_template = "admin/change_list_filter_sidebar.html"

    readonly_fields = ['posts_description', ]

    fieldsets = (
        ('', {
            'fields': ('case_code', 'case_status', 'posts_description'),
        }),
    )
    inlines = (FacebookPostInlineAdmin,)


# --------------------- Facebook Post
@admin.register(FacebookPost)
class FacebookPostAdmin(ImportExportModelAdmin):
    model = FacebookPost

    @admin.display(description='Posted')
    def admin_post_time(self, obj):
        return obj.post_time.strftime('%d/%m/%Y %H:%m')

    admin_post_time.admin_order_field = 'post_time'

    @admin.display(description='Post')
    def admin_post_text(self, obj):
        text = obj.post_text
        text = text.replace('\n', '<br/>')
        return mark_safe(
            '<p dir="rtl" style="direction: rtl; text-align: right; word-break: break-all; white-space: normal;">{0}</p>'.format(
                text))

    list_display = ['case_code', 'admin_post_time', 'admin_post_text', ]
    list_per_page = 20
    search_fields = ['case_code', 'post_id', 'post_text']
    readonly_fields = ['post_text', 'post_url', 'case_code', 'post_id', 'post_time', 'facebook_id', ]
    widgets = {'post_text': forms.Textarea(attrs={'dir': 'rtl', 'readonly': 'readonly'})}

    fieldsets = [
        (
            "Post",
            {
                "fields": ['post_text', 'post_url', 'post_id', 'post_time', 'facebook_id'],
            },
        ),
        (
            "Case",
            {
                "classes": ["collapse"],
                "fields": ["case_code"],
            },
        ),
    ]


# ---------------------- Facebook Photo

class ImagePreviewWidget(forms.widgets.FileInput):
    def render(self, name, value, attrs=None, **kwargs):
        input_html = super().render(name, value, attrs=None, **kwargs)
        if value:
            no_image_url = f'https://reunite-media.fra1.digitaloceanspaces.com/original/nophoto.jpg'

            img_html = mark_safe(
                f'<img onerror="this.src=\'{no_image_url}\'" src="{value}" '
                f'style="display: inline; width: 200px; max-width: 400px; height: auto;"/>')
            return f'{img_html}'
        return input_html


class FacebookPhotoAdminForm(forms.ModelForm):
    file_name = forms.CharField(disabled=True,
                                widget=forms.TextInput(attrs={'size': 60}))

    preview = forms.Field(widget=ImagePreviewWidget)

    class Meta:
        model = FacebookPhoto
        fields = ['post', 'url', 'media_id', 'ocr_text', 'file_name', 'preview']

    def get_initial_for_field(self, field, field_name):
        if field_name == 'file_name':
            if self.instance:
                return self.instance.photo_file_name()
            return None
        if field_name == 'preview':
            if self.instance:
                return self.instance.preview_url()
            return None
        return super().get_initial_for_field(field, field_name)


@admin.register(FacebookPhoto)
class FacebookPhotoAdmin(ImportExportModelAdmin):
    form = FacebookPhotoAdminForm
    list_display = ['post', 'url', 'photo_preview', 'face_boxes']
    list_per_page = 20
    search_fields = ['photo_image_url', 'url']

    # def has_change_permission(self, request, obj=None):
    #     return False

    formfield_overrides = {
        models.CharField: {'widget': forms.TextInput(attrs={'size': '60'})},
    }
    # https://stackoverflow.com/a/68850860
