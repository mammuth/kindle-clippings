from datetime import datetime, timedelta
from types import SimpleNamespace

from django.contrib.auth import get_user_model
from django.core import mail
from django.template.loader import render_to_string
from django.test import SimpleTestCase, TestCase
from django.utils import timezone

from clipping_manager.models import Book, Clipping, DonationConfig, EmailDelivery


class RandomClippingMailTemplateTests(SimpleTestCase):

    def render_mail(self, **context):
        clipping = SimpleNamespace(
            content='A highlighted passage.',
            book=SimpleNamespace(title='Example Book'),
        )
        default_context = {
            'clippings': [clipping],
        }
        default_context.update(context)

        return render_to_string('clipping_manager/email/random_clipping_mail.html', default_context)

    def test_donation_progress_is_hidden_by_default(self):
        html = self.render_mail()

        self.assertNotIn('background-color: #FF813F', html)
        self.assertNotIn('width="65%"', html)
        self.assertIn('href="https://reading-notes.com/en/support/"', html)

    def test_email_content_is_rendered_in_donation_section(self):
        html = self.render_mail(
            donation_email_content='<h1>Support <strong>Kindle Clippings</strong></h1><p>Help keep the project <em>alive</em>.</p>',
            show_donation_request=True,
        )

        self.assertIn('<title>Your Kindle Highlights</title>', html)
        self.assertIn('<h1 class="headline">Your Kindle Highlights Of Today</h1>', html)
        self.assertIn('<h1>Support <strong>Kindle Clippings</strong></h1>', html)
        self.assertIn('<p>Help keep the project <em>alive</em>.</p>', html)

    def test_donation_progress_renders_goal_and_percentage(self):
        html = self.render_mail(
            show_donation_request=True,
            donation_goal_amount='€500',
            donation_progress_percentage=65,
        )

        self.assertIn('<strong style="color: #333333;">65%</strong> of €500 goal', html)
        self.assertIn('width="65%"', html)
        self.assertIn('background-color: #FF813F', html)
        self.assertNotIn('Donation goal:', html)


class DonationConfigFrequencyTests(SimpleTestCase):

    def setUp(self):
        self.now = timezone.make_aware(datetime(2026, 3, 31, 12), timezone.utc)

    def test_never_and_every_email_frequencies(self):
        config = DonationConfig(request_frequency=DonationConfig.FREQUENCY_NEVER)
        self.assertFalse(config.should_show_request(None, now=self.now))

        config.request_frequency = DonationConfig.FREQUENCY_EVERY_EMAIL
        self.assertTrue(config.should_show_request(self.now, now=self.now))

    def test_weekly_frequency_is_due_after_seven_days(self):
        config = DonationConfig(request_frequency=DonationConfig.FREQUENCY_WEEKLY)

        self.assertFalse(config.should_show_request(self.now - timedelta(days=6), now=self.now))
        self.assertTrue(config.should_show_request(self.now - timedelta(days=7), now=self.now))

    def test_monthly_frequency_uses_calendar_month(self):
        config = DonationConfig(request_frequency=DonationConfig.FREQUENCY_MONTHLY)
        february_end = timezone.make_aware(datetime(2026, 2, 28, 12), timezone.utc)

        self.assertTrue(config.should_show_request(
            timezone.make_aware(datetime(2026, 1, 31, 12), timezone.utc),
            now=february_end,
        ))
        self.assertFalse(config.should_show_request(
            february_end,
            now=timezone.make_aware(datetime(2026, 3, 27, 12), timezone.utc),
        ))
        self.assertTrue(config.should_show_request(
            february_end,
            now=timezone.make_aware(datetime(2026, 3, 28, 12), timezone.utc),
        ))


class EmailDeliveryDonationTests(TestCase):

    def test_random_highlights_email_uses_global_donation(self):
        user = get_user_model().objects.create_user(
            username='reader@example.com',
            email='reader@example.com',
            password='password',
        )
        book = Book.objects.create(user=user, title='Example Book')
        Clipping.objects.create(user=user, book=book, content='A highlighted passage.')
        delivery = EmailDelivery.objects.create(user=user)
        DonationConfig.objects.create(
            email_content='<h1>Support <strong>Kindle Clippings</strong></h1><p>Help keep the project <em>alive</em>.</p>',
            request_frequency=DonationConfig.FREQUENCY_WEEKLY,
            goal_amount='€500',
            progress_percentage=65,
        )

        success = delivery.send_random_highlights_per_mail()

        self.assertTrue(success)
        delivery.refresh_from_db()
        self.assertIsNotNone(delivery.donation_request_last_sent_at)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Your Daily Kindle Highlights')
        self.assertIn('<p>Help keep the project <em>alive</em>.</p>', mail.outbox[0].body)
        self.assertIn('<strong style="color: #333333;">65%</strong> of €500 goal', mail.outbox[0].body)
        self.assertIn('width="65%"', mail.outbox[0].body)
        self.assertIn('href="https://reading-notes.com/en/support/"', mail.outbox[0].body)
        self.assertIn('href="https://reading-notes.com/"', mail.outbox[0].body)

    def test_random_highlights_email_omits_donation_before_frequency_is_due(self):
        user = get_user_model().objects.create_user(
            username='recent-reader@example.com',
            email='recent-reader@example.com',
            password='password',
        )
        book = Book.objects.create(user=user, title='Example Book')
        Clipping.objects.create(user=user, book=book, content='A highlighted passage.')
        donation_sent_at = timezone.now()
        delivery = EmailDelivery.objects.create(
            user=user,
            donation_request_last_sent_at=donation_sent_at,
        )
        DonationConfig.objects.create(
            email_content='<h1>Support Kindle Clippings</h1>',
            request_frequency=DonationConfig.FREQUENCY_WEEKLY,
            goal_amount='€500',
            progress_percentage=65,
        )

        success = delivery.send_random_highlights_per_mail()

        self.assertTrue(success)
        delivery.refresh_from_db()
        self.assertEqual(delivery.donation_request_last_sent_at, donation_sent_at)
        self.assertNotIn('Support Kindle Clippings', mail.outbox[0].body)
        self.assertNotIn('background-color: #FF813F', mail.outbox[0].body)
        self.assertIn('href="https://reading-notes.com/en/support/"', mail.outbox[0].body)
