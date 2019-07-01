from random import randint

from django.db import models
from django.db.models import Count


class ClippingQuerySetManager(models.QuerySet):

    def for_user(self, user):
        return self.filter(user=user)

    def random(self, limit=1):
        count = self.aggregate(count=Count('id'))['count']
        try:
            clippings = []
            for i in range(0, limit):
                random_index = randint(0, count - 1)
                clippings.append(self.all()[random_index])
                i += 1
            if limit == 1:
                return clippings[0]
            return clippings
        except ValueError:
            return self.none()


class BookQuerySetManager(models.QuerySet):

    def for_user(self, user):
        return self.filter(user=user)