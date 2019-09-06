from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _

from clipping_manager.managers import BookQuerySetManager


class Book(models.Model):

    objects = BookQuerySetManager().as_manager()

    user = models.ForeignKey(
        get_user_model(),
        blank=False,
        null=False,
        related_name='books',
    )

    title = models.CharField(
        verbose_name=_('Title'),
        max_length=500,
        blank=False,
    )

    author_name = models.CharField(
        verbose_name=_('Author'),
        max_length=500,
        blank=True,
    )

    class Meta:
        verbose_name = _('Book')
        verbose_name_plural = _('Books')
        ordering = ('title',)
        unique_together = ('title', 'user',)

    def __str__(self):
        if self.author_name:
            return f'{self.title} by {self.author_name}'
        return f'{self.title}'
