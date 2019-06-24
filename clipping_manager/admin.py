from django.contrib import admin

from clipping_manager.models import Clipping, Book


@admin.register(Clipping)
class ClippingAdmin(admin.ModelAdmin):
    pass


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    pass
