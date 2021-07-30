from django.db import models
from django.utils.translation import ugettext_lazy as _
from clipping_manager.managers import MyClippingsFileManager


class MyClippingsFile(models.Model):
    objects = MyClippingsFileManager()

    content = models.TextField(
        verbose_name=_('Content'),
        blank=False
    )

    uploaded_at = models.DateTimeField(
        verbose_name=_('Upload datetime'),
        auto_now_add=True,
        blank=False
    )

    language_header = models.CharField(
        verbose_name=_('Accept-Language header'),
        max_length=255,
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = _('MyClippings file')
        verbose_name_plural = _('MyClippings files')