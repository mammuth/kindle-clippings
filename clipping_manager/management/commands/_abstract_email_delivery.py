from clipping_manager.models import EmailDelivery
from django.db.models import Q
from django.utils import timezone


class AbstractEmailDeliveryCommand:

    def _get_delivery_interval(self):
        interval = getattr(self, 'INTERVAL', None)
        if not interval:
            raise NotImplementedError('You need to specify INTERVAL in your child class')
        else:
            return interval

    def get_queryset(self):
        # Make sure we return only email deliveries which have not been sent yet today.
        # This way, the command is idempotent.
        return EmailDelivery.objects.filter(
            Q(active=True, interval=self._get_delivery_interval())
            & (Q(last_delivery__isnull=True) | ~Q(last_delivery__day=timezone.now().day))
        ).select_related('user')

    def handle(self, *args, **options):
        qs = self.get_queryset()
        self.stdout.write(f"QuerySet size: {qs.count()}")

        successful_messages = 0
        for delivery in qs:
            self.stdout.write(f"Delivery: {delivery.user.email}")
            success = delivery.send_random_highlights_per_mail()
            if success:
                successful_messages += 1
        self.stdout.write(f'Sent {successful_messages} E-Mails.')
