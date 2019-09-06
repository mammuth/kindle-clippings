from django.contrib import admin

from clipping_manager.models import Clipping, Book, EmailDelivery


@admin.register(Clipping)
class ClippingAdmin(admin.ModelAdmin):
    list_filter = ('user', 'book', )
    search_fields = ('content', )


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_filter = ('user', )


@admin.register(EmailDelivery)
class EmailDeliveryAdmin(admin.ModelAdmin):
    search_fields = ('user', 'user__email')
    list_filter = ('user', )
    list_display = ('user', 'interval', 'last_delivery', )