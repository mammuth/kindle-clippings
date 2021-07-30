from random import randint

from django.db import models
from django.db.models import Count


class ClippingQuerySetManager(models.QuerySet):

    def for_user(self, user):
        return self.filter(user=user)

    def random(self, limit=None):
        count = self.aggregate(count=Count('id'))['count']
        try:
            clippings = []
            for i in range(0, limit or 1):
                random_index = randint(0, count - 1)
                clippings.append(self.all()[random_index])
                i += 1
            if limit is None:
                return clippings[0]  # return single item
            return clippings  # return list
        except ValueError:
            return self.none()


class BookQuerySetManager(models.QuerySet):

    def for_user(self, user):
        return self.filter(user=user)

class MyClippingsFileManager(models.Manager):
    def create_file(self, content, language_header):
        # Make sure file creation proceeds
        # even if language_header > field's max_length
        if language_header:
            language_header = language_header if len(language_header) <= 255 else language_header[:255]

        my_clippings_file = self.create(content=content, language_header=language_header)

        return my_clippings_file