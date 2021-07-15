import django_filters

from clipping_manager.models import Clipping, Book


class ClippingFilter(django_filters.FilterSet):
    """
    Attention: Filter should be passed a request object as argument!
    """
    content = django_filters.CharFilter(lookup_expr='icontains')
    book = django_filters.ModelChoiceFilter(
        queryset=lambda req: Book.objects.for_user(req.user).not_empty() if req is not None else Book.objects.none(),
    )

    class Meta:
        model = Clipping
        fields = ['book', 'content']