from django import forms
from django.utils.translation import ugettext_lazy as _


class UploadKindleClippingsForm(forms.Form):
    clippings_file = forms.FileField(
        label=_('Upload My Clippings.txt'),
        # required=True,
        widget=forms.FileInput(attrs={'accept': 'text/plain'})
    )


class UploadTextClippings(forms.Form):
    clippings_file = forms.FileField(
        label=_('Upload a *.txt file'),
        help_text=_('Individual clippings must have a blank line in between and only contain the clipping text itself '
                    '(book and author can be specified in the fields below)'),
        required=True,
        widget=forms.FileInput(attrs={'accept': 'text/plain'})
    )

    book_title = forms.CharField(
        required=False,
    )

    author = forms.CharField(
        required=False,
    )
