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


class BookEmailInclusionForm(forms.Form):
    """Form to toggle which books are included in email deliveries"""
    
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from clipping_manager.models import Book
        
        # Get user's books that have clippings, sorted by include_in_email (included first) then title
        books = Book.objects.for_user(user).not_empty().order_by('-include_in_email', 'title')
        
        for book in books:
            field_name = f'book_{book.id}'
            self.fields[field_name] = forms.BooleanField(
                label=str(book),
                required=False,
                initial=book.include_in_email,
                widget=forms.CheckboxInput(attrs={'class': 'book-toggle-checkbox'})
            )
    
    def save(self, user):
        """Save the book inclusion settings"""
        from clipping_manager.models import Book
        
        for field_name, value in self.cleaned_data.items():
            if field_name.startswith('book_'):
                book_id = int(field_name.replace('book_', ''))
                Book.objects.filter(id=book_id, user=user).update(include_in_email=value)

