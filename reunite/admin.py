from django.contrib import admin
from django import forms
from django.db import models
from import_export.admin import ImportExportModelAdmin
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
    fields = ['post', 'case']
    readonly_fields = ['post_preview',]


class CaseAdmin(ImportExportModelAdmin):
    form = CaseAdminForm
    model = Case
    list_display = ['case_code', 'fb_posts', 'description', 'case_status']
    list_editable = ['case_status']
    list_filter = ['case_status']
    search_fields = ['case_code', 'description']
    verbose_name = _('Case')
    verbose_name_plural = _('Cases')
    # change_list_template = "admin/change_list_filter_sidebar.html"

    def fb_posts(self, obj):
        return "\n".join([p.post_id for p in obj.posts.all()])

    fieldsets = (
        ('', {
            'fields': ('case_code',),
        }),
        ('Facebook Post/Description', {
            'classes': ('grp-collapse grp-closed',),
            'fields': ('description',),
        }),
        ('Status', {
            'classes': ('grp-collapse grp-open',),
            'fields': ('case_status',),
        }),
    )
    inlines = (FacebookPostInlineAdmin,)


admin.site.register(Case, CaseAdmin)


# --------------------- Facebook Post
class FacebookPostAdmin(ImportExportModelAdmin):
    model = FacebookPost
    list_display = ['case_code', 'post_id', 'post_time', 'post_text', ]
    search_fields = ['case_code', 'post_id', 'post_text']
    readonly_fields = ['post_text', 'post_url', 'case_code', 'post_id', 'post_time', 'facebook_id', ]
    widgets = {'post_text': forms.Textarea(attrs={'dir': 'rtl', 'readonly': 'readonly'})}


admin.site.register(FacebookPost, FacebookPostAdmin)


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


class FacebookPhotoAdmin(ImportExportModelAdmin):
    form = FacebookPhotoAdminForm
    list_display = ['post', 'url']
    search_fields = ['post']
    formfield_overrides = {
        models.CharField: {'widget': forms.TextInput(attrs={'size': '60'})},
    }
    # https://stackoverflow.com/a/68850860


admin.site.register(FacebookPhoto, FacebookPhotoAdmin)
