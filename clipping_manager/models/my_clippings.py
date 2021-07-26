from django.db import models
from django.utils.translation import ugettext_lazy as _

class MyClippingsFiles(models.Model):
    content = models.TextField(
        verbose_name=_('Content'),
        blank=False
    )

    timestamp = models.DateTimeField(
        verbose_name=_('Timestamp'),
        auto_now_add=True,
        blank=False
    )

    class Meta:
        verbose_name = _('MyClippings file')
        verbose_name_plural = _('MyClippings files')