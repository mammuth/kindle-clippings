# -*- coding: utf-8 -*-

INSTALLED_ADDONS = [
    # <INSTALLED_ADDONS>  # Warning: text inside the INSTALLED_ADDONS tags is auto-generated. Manual changes will be overwritten.
    'aldryn-addons',
    'aldryn-django',
    'aldryn-sso',
    'aldryn-django-cms',
    'djangocms-file',
    'djangocms-googlemap',
    'djangocms-history',
    'djangocms-link',
    'djangocms-picture',
    'djangocms-snippet',
    'djangocms-style',
    'djangocms-text-ckeditor',
    'djangocms-video',
    'django-filer',
    # </INSTALLED_ADDONS>
]

import aldryn_addons.settings
aldryn_addons.settings.load(locals())


INSTALLED_APPS.extend([
    'crispy_forms',
    'django_extensions',
    'allauth',
    'allauth.socialaccount',
    'allauth.account',

    'clipping_manager',
])

# Allauth settings
AUTHENTICATION_BACKENDS.append(['allauth.account.auth_backends.AuthenticationBackend'])
LOGIN_URL = '/accounts/login/'  # Override divio login
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = False


CRISPY_TEMPLATE_PACK = 'bootstrap4'

DJANGOCMS_LINK_TEMPLATES = [
    ('button', 'Button'),
    ('button_outline', 'Button Outline'),
]