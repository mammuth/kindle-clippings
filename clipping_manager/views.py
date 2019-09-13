import logging
import traceback
from codecs import EncodedFile

from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q, Count
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, FormView, ListView, UpdateView
from django.utils.translation import ugettext_lazy as _
from django.views.generic.base import View

from clipping_manager.clipping_parser import kindle_clipping_parser, plaintext_parser
from clipping_manager.filters import ClippingFilter
from clipping_manager.forms import UploadKindleClippingsForm, UploadTextClippings
from clipping_manager.models import Clipping, Book
from clipping_manager.models.email_delivery import EmailDelivery

logger = logging.getLogger(__name__)


class DashboardView(TemplateView):
    template_name = 'clipping_manager/dashboard.html'


class ClippingsBrowseView(ListView):
    template_name = 'clipping_manager/browse.html'
    context_object_name = 'clippings'
    model = Clipping
    paginate_by = 15

    def dispatch(self, request, *args, **kwargs):
        self.filter = None  # Will be set in get_queryset()
        return super(ClippingsBrowseView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(ClippingsBrowseView, self).get_context_data(**kwargs)
        ctx['clippings_count'] = Clipping.objects.for_user(self.request.user).count()
        ctx['books_count'] = Book.objects.for_user(self.request.user).count()
        ctx['filter'] = self.filter
        return ctx

    def get_queryset(self):
        qs = Clipping.objects.select_related('book').for_user(user=self.request.user)
        self.filter = ClippingFilter(self.request.GET, request=self.request, queryset=qs)
        return self.filter.qs.distinct()


class UploadMyClippingsFileView(FormView):
    form_class = UploadKindleClippingsForm
    template_name = 'clipping_manager/upload_kindle_clippings_file.html'
    success_url = reverse_lazy('clipping_manager:dashboard')

    def form_valid(self, form):
        if 'clippings_file' not in self.request.FILES:
            messages.add_message(self.request, messages.ERROR, _('Could not process the uploaded file'))
            return super(UploadMyClippingsFileView, self).form_valid(form)

        try:
            clippings_file = EncodedFile(self.request.FILES['clippings_file'], 'utf-8')
            clippings_file_content = clippings_file.read()
            clips = kindle_clipping_parser.get_clips_from_text(clippings_file_content)
            user = self.request.user
            num_books = 0
            num_clippings = 0
            for book, clippings in clips.items():
                book, created = Book.objects.get_or_create(
                    user=user,
                    title=book,
                )
                num_books += 1
                for clip_content in clippings:
                    Clipping.objects.get_or_create(
                        user=user,
                        content=clip_content,
                        defaults={
                            'book': book,
                        }
                    )
                    num_clippings += 1
        except Exception as e:
            logger.error(f'Error processing a clippings file.', exc_info=True)
            messages.add_message(
                self.request,
                messages.ERROR,
                _('Couldn\'t process your Clippings. The developer is informed, please try again in a couple of days!')
            )
        else:
            messages.add_message(
                self.request,
                messages.SUCCESS,
                _('Successfully uploaded {num_clippings} clippings from {num_books} books').format(
                    num_clippings=num_clippings,
                    num_books=num_books,
                )
            )

        return super(UploadMyClippingsFileView, self).form_valid(form)


class UploadTextFileClippingsView(FormView):
    """
    View for uploading generic text-file clippings (blank line separated clippings)
    """
    form_class = UploadTextClippings
    template_name = 'clipping_manager/upload_plaintext_clippings_file.html'
    success_url = reverse_lazy('clipping_manager:upload-plaintext')

    def form_valid(self, form):
        if 'clippings_file' not in self.request.FILES:
            messages.add_message(self.request, messages.ERROR, _('Could not process the uploaded file'))
            return super(UploadTextFileClippingsView, self).form_valid(form)

        clippings_file = EncodedFile(self.request.FILES['clippings_file'], 'utf-8')
        clippings_file_content = clippings_file.read()
        clips = plaintext_parser.get_clips_from_text(clippings_file_content)
        user = self.request.user
        num_clippings = 0

        try:
            book_title = form.cleaned_data.get('book_title', None)
            book = None
            if book_title:
                book, __ = Book.objects.get_or_create(
                    user=user,
                    title=book_title,
                    defaults={
                        'author_name': form.cleaned_data.get('author', None),
                    },
                )

            for clip_content in clips:
                __, created = Clipping.objects.get_or_create(
                    user=user,
                    content=clip_content,
                    defaults={
                        'book': book,
                    }
                )
                if created:
                    num_clippings += 1
        except Exception as e:
            logger.error(f'Error processing a clippings file.', exc_info=True)
            messages.add_message(
                self.request,
                messages.ERROR,
                _('Couldn\'t process all clippings. The developer is informed, please try again in a couple of days!')
            )
        else:
            messages.add_message(
                self.request,
                messages.SUCCESS,
                _('Successfully uploaded {num_clippings} clippings.').format(
                    num_clippings=num_clippings,
                )
            )
        return super(UploadTextFileClippingsView, self).form_valid(form)


class EmailDeliveryView(SuccessMessageMixin, UpdateView):
    model = EmailDelivery
    fields = ['active', 'interval', 'number_of_highlights']
    template_name = 'clipping_manager/email_delivery_configuration.html'
    success_url = reverse_lazy('clipping_manager:email-delivery')
    success_message =  _('Updated your email delivery settings!')

    def get_object(self, queryset=None):
        delivery, _ = EmailDelivery.objects.get_or_create(user=self.request.user)
        return delivery


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
        ctx['user_count_with_uploads'] = User.objects.exclude(clippings__isnull=True).count()
        ctx['user_count_total'] = User.objects.count()
        ctx['books_count'] = Book.objects.count()
        ctx['clippings_count'] = Clipping.objects.count()
        ctx['email_deliveries_count'] = EmailDelivery.objects.filter(active=True).count()

        user_clippings_counts = User.objects.exclude(clippings__isnull=True).values('email').annotate(Count('clippings'))
        user_clippings_counts = sorted(
            list(user_clippings_counts),
            key=lambda tuple: tuple['clippings__count'],
            reverse=True
        )
        ctx['user_clippings_tuple'] = user_clippings_counts[:30]
        return ctx


@method_decorator(csrf_exempt, name='dispatch')
class AbstractSendEmailDeliveriesView(View):
    # ToDo: We should add some kind of authorization here
    def post(self, request, *args, **kwargs):
        qs = self.get_queryset()
        successful_messages = 0
        for delivery in qs:
            success = delivery.send_random_highlights_per_mail()
            if success:
                successful_messages += 1

        response_text = f'Sent {successful_messages} mails.'
        return HttpResponse(content=response_text.encode('utf-8'))

    def get_queryset(self):
        # Make sure we return only email deliveries which have not been sent yet today
        # (this way the view cannot be abused that easily)
        return EmailDelivery.objects.filter(
            Q(active=True)
            & (Q(last_delivery__isnull=True) | ~Q(last_delivery__day=timezone.now().day))
        ).select_related('user')


class DailyEmailDeliveryView(AbstractSendEmailDeliveriesView):
    def get_queryset(self):
        qs = super(DailyEmailDeliveryView, self).get_queryset().filter(interval=EmailDelivery.INTERVAL_DAILY)
        return qs


class BiweeklyEmailDeliveryView(AbstractSendEmailDeliveriesView):
    def get_queryset(self):
        return super(BiweeklyEmailDeliveryView, self).get_queryset().filter(interval=EmailDelivery.INTERVAL_BIWEEKLY)


class WeeklyEmailDeliveryView(AbstractSendEmailDeliveriesView):
    def get_queryset(self):
        return super(WeeklyEmailDeliveryView, self).get_queryset().filter(interval=EmailDelivery.INTERVAL_WEEKLY)
