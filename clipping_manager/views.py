import logging

from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q, Count
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, FormView, ListView
from django.utils.translation import ugettext_lazy as _

from clipping_manager.clipping_parser import get_clips_from_text
from clipping_manager.forms import UploadClippingForm
from clipping_manager.models import Clipping, Book

logger = logging.getLogger(__name__)


class DashboardView(ListView):
    template_name = 'clipping_manager/dashboard.html'
    context_object_name = 'clippings'
    model = Clipping
    paginate_by = 15

    def get_context_data(self, **kwargs):
        ctx = super(DashboardView, self).get_context_data(**kwargs)
        ctx['clippings_count'] = Clipping.objects.for_user(self.request.user).count()
        ctx['books_count'] = Book.objects.for_user(self.request.user).count()
        return ctx

    def get_queryset(self):
        return Clipping.objects.select_related('book').for_user(user=self.request.user)


class UploadMyClippingsFileView(FormView):
    form_class = UploadClippingForm
    template_name = 'clipping_manager/upload_clippings_file.html'
    success_url = reverse_lazy('clipping_manager:dashboard')

    def form_valid(self, form):
        if 'clippings_file' not in self.request.FILES:
            messages.add_message(self.request, messages.ERROR, _('Could not process the uploaded file'))
            return super(UploadMyClippingsFileView, self).form_valid(form)

        try:
            clippings_file_content = self.request.FILES['clippings_file'].read().decode('utf-8')
            clips = get_clips_from_text(clippings_file_content)
            user = self.request.user
            for book, clippings in clips.items():
                book, created = Book.objects.get_or_create(
                    user=user,
                    title=book,
                )
                for clip_content in clippings:
                    Clipping.objects.get_or_create(
                        user=user,
                        book=book,
                        content=clip_content,
                    )
        except Exception as e:
            logger.error(f'Error processing a clippings file.\n{e}')
            messages.add_message(self.request, messages.ERROR, _('Could not process the uploaded file. The developer is informed, please try again in a couple of days!'))
        else:
            messages.add_message(self.request, messages.SUCCESS, _('Successfully uploaded My Clippings.txt'))

        return super(UploadMyClippingsFileView, self).form_valid(form)


class RandomClippingView(TemplateView):
    template_name = 'clipping_manager/random_clipping.html'

    def get(self, request, *args, **kwargs):
        clipping = Clipping.objects.select_related('book').for_user(self.request.user).random()
        self.clipping = clipping
        if not clipping:
            messages.add_message(self.request, messages.WARNING, _('You need to import your highlights first!'))
            return redirect('clipping_manager:upload')
        return super(RandomClippingView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(RandomClippingView, self).get_context_data(**kwargs)
        ctx['clipping'] = self.clipping
        return ctx


class RandomClippingFullscreenView(RandomClippingView):
    template_name = 'clipping_manager/random_clipping_fullscreen.html'


class AdminStatisticsView(TemplateView):
    template_name = 'clipping_manager/admin_statistics.html'

    def get_context_data(self, **kwargs):
        ctx = super(AdminStatisticsView, self).get_context_data(**kwargs)
        ctx['user_count'] = User.objects.count()
        ctx['books_count'] = Book.objects.count()
        ctx['clippings_count'] = Clipping.objects.count()

        user_clippings_counts = User.objects.values('email').annotate(Count('clippings'))
        user_clippings_counts = sorted(
            list(user_clippings_counts),
            key=lambda tuple: tuple['clippings__count'],
            reverse=True
        )
        ctx['user_clippings_tuple'] = user_clippings_counts[:30]
        return ctx
