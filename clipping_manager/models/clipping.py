from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _

from clipping_manager.managers import ClippingQuerySetManager


class Clipping(models.Model):

    objects = ClippingQuerySetManager().as_manager()

    user = models.ForeignKey(
        get_user_model(),
        blank=False,
        null=False,
        related_name='clippings',
    )

    book = models.ForeignKey(
        'Book',
        verbose_name='Book',
        blank=False,
        null=False,
        on_delete=models.CASCADE,
    )

    content = models.TextField(
        verbose_name=_('Content'),
        blank=False,
    )

    class Meta:
        verbose_name = _('Clipping')
        verbose_name_plural = _('Clippings')
        ordering = ('book',)
        unique_together = ('user', 'book', 'content',)

    def __str__(self):
        return f'{self.content[:50]}...'
