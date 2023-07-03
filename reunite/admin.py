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
        readonly_fields = ['description', ]
        widgets = {'description': forms.Textarea(attrs={'dir': 'rtl', 'readonly': 'readonly'})}


class FacebookPostInlineAdmin(admin.TabularInline):
    model = Case.posts.through
    extra = 0
    verbose_name = _('Facebook Post')
    verbose_name_plural = _('Facebook Posts')
    fields = ['post', 'case', 'post_preview']
    readonly_fields = ['post_preview',]


@admin.register(Case)
class CaseAdmin(ImportExportModelAdmin, RelatedFieldAdmin):
    form = CaseAdminForm
    model = Case

    list_display = ['case_code', 'fb_posts', 'description', 'case_status']
    list_editable = ['case_status']
    list_filter = ['case_status']
    search_fields = ['case_code', 'description']
    verbose_name = _('Case')
    verbose_name_plural = _('Cases')
    list_per_page = 20
    # change_list_template = "admin/change_list_filter_sidebar.html"

    fieldsets = (
        ('', {
            'fields': ('case_code', 'case_status'),
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
        return mark_safe('<p dir="rtl" style="direction: rtl; text-align: right; word-break: break-all; white-space: normal;">{0}</p>'.format(text))

    list_display = ['case_code', 'admin_post_time', 'admin_post_text', ]
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

class FacebookPhotoAdminForm(forms.ModelForm):
    file_name = forms.CharField(disabled=True,
                                widget=forms.TextInput(attrs={'size': 60}))

    class Meta:
        model = FacebookPhoto
        fields = ['post', 'url', 'media_id', 'ocr_text', 'file_name']

    def get_initial_for_field(self, field, field_name):
        if field_name == 'file_name':
            if self.instance:
                return self.instance.photo_file_name()
            return None
        return super().get_initial_for_field(field, field_name)


@admin.register(FacebookPhoto)
class FacebookPhotoAdmin(ImportExportModelAdmin):
    form = FacebookPhotoAdminForm
    list_display = ['post', 'url', 'photo_preview']
    search_fields = ['post']
    formfield_overrides = {
        models.CharField: {'widget': forms.TextInput(attrs={'size': '60'})},
    }
    # https://stackoverflow.com/a/68850860

