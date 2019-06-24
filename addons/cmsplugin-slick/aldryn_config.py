from aldryn_client import forms

class Form(forms.BaseForm):
    slick_cdn = forms.CharField ('Replaced default slick cdn url', required=False)

    def to_settings(self, data, settings):
        if data['slick_cdn']:
            settings['SLICK_CDN'] = data['slick_cdn']

        return settings