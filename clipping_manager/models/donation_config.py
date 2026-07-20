from calendar import monthrange
from datetime import timedelta

from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from djangocms_text_ckeditor.fields import HTMLField


class DonationConfig(models.Model):
    SINGLETON_ID = 1

    FREQUENCY_NEVER = 'never'
    FREQUENCY_EVERY_EMAIL = 'every_email'
    FREQUENCY_WEEKLY = 'weekly'
    FREQUENCY_MONTHLY = 'monthly'
    FREQUENCY_CHOICES = (
        (FREQUENCY_NEVER, _('Never')),
        (FREQUENCY_EVERY_EMAIL, _('Every email')),
        (FREQUENCY_WEEKLY, _('Weekly')),
        (FREQUENCY_MONTHLY, _('Monthly')),
    )

    email_content = HTMLField(
        verbose_name=_('Email content'),
        blank=True,
        default='',
    )

    request_frequency = models.CharField(
        verbose_name=_('Donation request frequency'),
        max_length=20,
        choices=FREQUENCY_CHOICES,
        blank=False,
        default=FREQUENCY_NEVER,
    )

    goal_amount = models.CharField(
        verbose_name=_('Goal amount'),
        max_length=100,
        blank=False,
        default='',
    )

    progress_percentage = models.PositiveSmallIntegerField(
        verbose_name=_('Progress percentage'),
        blank=False,
        default=0,
    )

    class Meta:
        verbose_name = 'Donation configuration'
        verbose_name_plural = 'Donation configuration'

    def save(self, *args, **kwargs):
        self.pk = self.SINGLETON_ID
        self.progress_percentage = max(0, min(int(self.progress_percentage or 0), 100))
        super(DonationConfig, self).save(*args, **kwargs)

    @classmethod
    def current(cls):
        return cls.objects.filter(pk=cls.SINGLETON_ID).first()

    def should_show_request(self, last_sent_at, now=None):
        if self.request_frequency == self.FREQUENCY_NEVER:
            return False
        if self.request_frequency == self.FREQUENCY_EVERY_EMAIL or last_sent_at is None:
            return True

        now = now or timezone.now()
        if self.request_frequency == self.FREQUENCY_WEEKLY:
            return now >= last_sent_at + timedelta(days=7)

        year = last_sent_at.year + last_sent_at.month // 12
        month = last_sent_at.month % 12 + 1
        day = min(last_sent_at.day, monthrange(year, month)[1])
        return now >= last_sent_at.replace(year=year, month=month, day=day)

    def __str__(self):
        return 'Donation configuration'
