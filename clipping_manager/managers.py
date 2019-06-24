from random import randint

from django.db import models
from django.db.models import Count

from clipping_manager.models import Clipping


class ClippingQuerySetManager(models.QuerySet):

    def for_user(self, user):
        return self.filter(user=user)

    def random(self) -> Clipping:
        count = self.aggregate(count=Count('id'))['count']
        random_index = randint(0, count - 1)
        try:
            clip = self.all()[random_index]
        except ValueError:
            return self.none()


class BookQuerySetManager(models.QuerySet):

    def for_user(self, user):
        return self.filter(user=user)