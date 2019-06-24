# -*- coding: utf-8 -*-
from django.conf.urls import url, include
from aldryn_django.utils import i18n_patterns
import aldryn_addons.urls


urlpatterns = [
    url(r'^accounts/', include('allauth.urls')),
] + aldryn_addons.urls.patterns() + i18n_patterns(
    *aldryn_addons.urls.i18n_patterns()  # MUST be the last entry!
)
