from django.core.management.base import BaseCommand

from clipping_manager.management.commands._abstract_email_delivery import AbstractEmailDeliveryCommand
from clipping_manager.models import EmailDelivery


class Command(AbstractEmailDeliveryCommand, BaseCommand):
    help = "Sends all configured bi-weekly email deliveries"
    INTERVAL = EmailDelivery.INTERVAL_BIWEEKLY
