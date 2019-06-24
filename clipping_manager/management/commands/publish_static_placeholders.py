from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Force publishing all StaticPlaceholders"

    def handle(self, *args, **options):
        self.stdout.write('publishing staticplaceholders')

        from cms.models import StaticPlaceholder
        from django.conf import settings

        for placeholder in StaticPlaceholder.objects.all():
            for lang in settings.LANGUAGES:
                placeholder.publish(None, lang[0], force=True)
        self.stdout.write('all done')
