from django.db import models
from django.utils.translation import ugettext_lazy as _
from clipping_manager.managers import MyClippingsFilesManager


class MyClippingsFiles(models.Model):
    objects = MyClippingsFilesManager()

    content = models.TextField(
        verbose_name=_('Content'),
        blank=False
    )

    timestamp = models.DateTimeField(
        verbose_name=_('Timestamp'),
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