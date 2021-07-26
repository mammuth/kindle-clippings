from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db import models

from clipping_manager.models import Clipping, Book, EmailDelivery, MyClippingsFiles


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

@admin.register(MyClippingsFiles)
class MyClippingsFilesAdmin(admin.ModelAdmin):
    search_fields = ('language_header',)
    list_display = ('language_header', 'timestamp',)


# Custom UserAdmin
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'date_joined', 'get_num_clippings', )
    list_filter = ('date_joined', )
    ordering = ('-date_joined', )

    def get_queryset(self, request):
        qs = super(UserAdmin, self).get_queryset(request)
        qs = qs.annotate(models.Count('clippings'))
        return qs

    def get_num_clippings(self, obj):
        return obj.clippings__count
    get_num_clippings.short_description = 'Number of clippings'
    get_num_clippings.admin_order_field = 'clippings__count'


admin.site.unregister(get_user_model())
admin.site.register(get_user_model(), UserAdmin)