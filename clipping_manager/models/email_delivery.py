import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage, send_mail
from django.db import models
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from clipping_manager.models import Clipping

logger = logging.getLogger(__name__)


class EmailDelivery(models.Model):
    user = models.OneToOneField(
        get_user_model(),
        verbose_name=_('User'),
        blank=False,
        null=False,
    )

    active = models.BooleanField(
        verbose_name=_('Active'),
        blank=False,
        default=True,
    )

    INTERVAL_DAILY = 1
    INTERVAL_BIWEEKLY = 2
    INTERVAL_WEEKLY = 3

    INTERVAL_CHOICES = (
        (INTERVAL_DAILY, _('Daily')),
        (INTERVAL_BIWEEKLY, _('Bi-weekly')),
        (INTERVAL_WEEKLY, _('Weekly')),
    )

    interval = models.PositiveSmallIntegerField(
        verbose_name=_('Interval'),
        choices=INTERVAL_CHOICES,
        blank=False,
        default=INTERVAL_DAILY,
    )

    number_of_highlights = models.PositiveSmallIntegerField(
        verbose_name=_('Number of highlights to be sent per mail'),
        blank=False,
        null=False,
        default=1,
    )

    last_delivery = models.DateTimeField(
        verbose_name=_('Last successful delivery'),
        blank=True,
        null=True,
    )


    class Meta:
        verbose_name = 'Email delivery'
        verbose_name_plural = 'Email deliveries'

    def __str__(self):
        return f'E-Mail Delivery for {self.user.email} {self.get_interval_display()}'

    def send_random_highlights_per_mail(self):
        # ToDo: Use shared email connection
        # ToDo: Use external service?
        if self.user.email:
            try:
                random_clipping = Clipping.objects.for_user(self.user).for_email_delivery().random(limit=self.number_of_highlights)

                if not random_clipping:
                    return False

                rendered_highlight_mail = render_to_string('clipping_manager/email/random_clipping_mail.html', {
                    'clippings': random_clipping
                })
                msg = EmailMessage(
                    _('Your Daily Kindle Highlights'),
                    rendered_highlight_mail,
                    settings.DEFAULT_FROM_EMAIL,
                    [self.user.email],
                )
                msg.content_subtype = 'html'
                msg.send()
            except Exception as e:
                logger.error(f'Error sending highlights per mail. Exception:\n{repr(e)}')
                return False
            else:
                # Update last_delivery flag on model instance
                self.last_delivery = timezone.now()
                self.save()
                return True
        return False
