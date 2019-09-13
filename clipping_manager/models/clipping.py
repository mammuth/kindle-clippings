from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _
import hashlib

from clipping_manager.managers import ClippingQuerySetManager


class Clipping(models.Model):

    objects = ClippingQuerySetManager().as_manager()

    #
    # Base fields
    #

    user = models.ForeignKey(
        get_user_model(),
        blank=False,
        null=False,
        related_name='clippings',
    )

    content = models.TextField(
        verbose_name=_('Content'),
        blank=False,
    )

    # This field is used for the unique_together constraint, as the content might be arbitrary large (see https://code.djangoproject.com/ticket/14904)  # noqa
    content_hash = models.CharField(
        verbose_name=_('Hash of the clipping'),
        max_length=100,
        blank=False,
        null=True,
    )

    #
    # Optional fields
    #

    book = models.ForeignKey(
        'Book',
        verbose_name='Book',
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )

    author_name = models.CharField(
        verbose_name=_('Author'),
        blank=True,
        null=True,
        max_length=500,
    )

    url = models.URLField(
        verbose_name=_('URL'),
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = _('Clipping')
        verbose_name_plural = _('Clippings')
        ordering = ('user', 'book', 'author_name',)
        unique_together = ('user', 'book', 'content_hash',)

    def __str__(self):
        return f'{self.content[:100]}...'

    def save(self, *args, **kwargs):

        # Generate hash of the content and store it in content_hash
        # This is used for unique_together which is not possible with content directly due ot its arbitrary length
        content_md5_obj = hashlib.md5(self.content.encode('utf-8'))
        self.content_hash = content_md5_obj.hexdigest()

        super(Clipping, self).save(*args, **kwargs)

    def get_author_name(self) -> str:
        if self.author_name:
            return self.author_name
        elif self.book:
            return self.book.author_name or ''
        return ''
