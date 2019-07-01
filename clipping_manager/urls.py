from django.conf.urls import url
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required

from clipping_manager.views import UploadMyClippingsFileView, RandomClippingView, RandomClippingFullscreenView, \
    DashboardView, AdminStatisticsView, cron_daily_view

urlpatterns = [
    url(r'^$', login_required(DashboardView.as_view()), name='dashboard'),
    url(r'^upload/$', login_required(UploadMyClippingsFileView.as_view()), name='upload'),
    url(r'^random/$', login_required(RandomClippingView.as_view()), name='random-clipping'),
    url(r'^random-fullscreen/$', login_required(RandomClippingFullscreenView.as_view()), name='random-clipping-fullscreen'),
    url(r'^statistics/$', staff_member_required(AdminStatisticsView.as_view()), name='statistics'),
    url(r'^cron/daily/$', cron_daily_view, name='cron-daily'),
]