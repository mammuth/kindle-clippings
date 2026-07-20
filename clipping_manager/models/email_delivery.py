import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage, send_mail
from django.db import models
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from clipping_manager.models.clipping import Clipping
from clipping_manager.models.donation_config import DonationConfig

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

    donation_request_last_sent_at = models.DateTimeField(
        verbose_name=_('Donation request last sent at'),
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

                donation_config = DonationConfig.current()
                show_donation_request = (
                    donation_config.should_show_request(self.donation_request_last_sent_at)
                    if donation_config else False
                )

                rendered_highlight_mail = render_to_string('clipping_manager/email/random_clipping_mail.html', {
                    'clippings': random_clipping,
                    'donation_email_content': donation_config.email_content if donation_config else '',
                    'show_donation_request': show_donation_request,
                    'donation_goal_amount': donation_config.goal_amount if donation_config else '',
                    'donation_progress_percentage': donation_config.progress_percentage if donation_config else 0,
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
                if show_donation_request:
                    self.donation_request_last_sent_at = self.last_delivery
                self.save()
                return True
        return False
