from django.conf.urls import url
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required

from clipping_manager.views import UploadMyClippingsFileView, RandomClippingView, RandomClippingFullscreenView, \
    DashboardView, AdminStatisticsView, EmailDeliveryView, DailyEmailDeliveryView, BiweeklyEmailDeliveryView, \
    WeeklyEmailDeliveryView, ClippingsManagementView

urlpatterns = [
    url(r'^$', login_required(DashboardView.as_view()), name='dashboard'),
    url(r'^manage/$', login_required(ClippingsManagementView.as_view()), name='management'),
    url(r'^upload/$', login_required(UploadMyClippingsFileView.as_view()), name='upload'),
    url(r'^email-delivery/$', login_required(EmailDeliveryView.as_view()), name='email-delivery'),
    url(r'^random/$', login_required(RandomClippingView.as_view()), name='random-clipping'),
    url(r'^random-fullscreen/$', login_required(RandomClippingFullscreenView.as_view()), name='random-clipping-fullscreen'),
    url(r'^statistics/$', staff_member_required(AdminStatisticsView.as_view()), name='statistics'),
    url(r'^cron/daily/$', DailyEmailDeliveryView.as_view(), name='cron-daily'),
    url(r'^cron/weekly/$', WeeklyEmailDeliveryView.as_view(), name='cron-weekly'),
    url(r'^cron/biweekly/$', BiweeklyEmailDeliveryView.as_view(), name='cron-biweekly'),
]