from random import randint

from django.db import models
from django.db.models import Count


class ClippingQuerySet(models.QuerySet):

    def for_user(self, user):
        return self.filter(user=user)

    def random(self, limit):
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


class ExistingClippingsManager(models.Manager):
    
    def get_queryset(self):
        return ClippingQuerySet(self.model, using=self._db).exclude(deleted=True)
    
    def for_user(self, user):
        return self.get_queryset().for_user(user)

    def random(self, limit=None):
        return self.get_queryset().random(limit)


class AllClippingsManager(ExistingClippingsManager):

    def get_queryset(self):
        return ClippingQuerySet(self.model, using=self._db)


class BookQuerySetManager(models.QuerySet):

    def for_user(self, user):
        return self.filter(user=user)

    def not_empty(self):
        book_count = self.annotate(clippings_count = Count('clippings'))
        return book_count.filter(clippings_count__gt=0)