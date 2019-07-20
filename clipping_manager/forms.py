from django import forms
from django.utils.translation import ugettext_lazy as _


class UploadClippingForm(forms.Form):
    clippings_file = forms.FileField(
        label=_('Upload My Clippings.txt'),
        # required=True,
        widget=forms.FileInput(attrs={'accept': 'text/plain'})
    )
