from django.conf.urls import url
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required

from clipping_manager.views import UploadMyClippingsFileView, RandomClippingView, RandomClippingFullscreenView, \
    DashboardView, AdminStatisticsView, EmailDeliveryView, DailyEmailDeliveryView, BiweeklyEmailDeliveryView, \
    WeeklyEmailDeliveryView, ClippingsBrowseView, UploadTextFileClippingsView, PersonalStatisticsView, BooksView, \
    DeleteClipping

urlpatterns = [
    url(r'^$', login_required(DashboardView.as_view()), name='dashboard'),
    url(r'^browse/$', login_required(ClippingsBrowseView.as_view()), name='browse'),
    url(r'^delete-clipping/$', login_required(DeleteClipping.as_view()), name='delete-clipping'),
    url(r'^books/$', login_required(BooksView.as_view()), name='books'),
    url(r'^upload/$', login_required(UploadMyClippingsFileView.as_view()), name='upload'),
    url(r'^upload-plaintext/$', login_required(UploadTextFileClippingsView.as_view()), name='upload-plaintext'),
    url(r'^email-delivery/$', login_required(EmailDeliveryView.as_view()), name='email-delivery'),
    url(r'^statistics/$', login_required(PersonalStatisticsView.as_view()), name='statistics'),
    url(r'^random/$', login_required(RandomClippingView.as_view()), name='random-clipping'),
    url(r'^random-fullscreen/$', login_required(RandomClippingFullscreenView.as_view()), name='random-clipping-fullscreen'),
    url(r'^admin-statistics/$', staff_member_required(AdminStatisticsView.as_view()), name='admin-statistics'),
    url(r'^cron/daily/$', DailyEmailDeliveryView.as_view(), name='cron-daily'),
    url(r'^cron/weekly/$', WeeklyEmailDeliveryView.as_view(), name='cron-weekly'),
    url(r'^cron/biweekly/$', BiweeklyEmailDeliveryView.as_view(), name='cron-biweekly'),
]