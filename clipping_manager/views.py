import logging
import statistics
import traceback
from codecs import EncodedFile
from collections import Counter

from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.db import models
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
from clipping_manager.models import Clipping, Book, MyClippingsFile
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
        ctx['contains'] = self.request.GET.get('content', '')
        ctx['filter'] = self.filter
        return ctx

    def get_queryset(self):
        qs = Clipping.objects.select_related('book').for_user(user=self.request.user)
        self.filter = ClippingFilter(self.request.GET, request=self.request, queryset=qs)
        return self.filter.qs.distinct()

class DeleteClipping(View):
    http_method_names = ['post']

    def post(self, request):
        clipping_id = int(request.POST['clipping-id'])
        clipping_to_delete = Clipping.objects.get(id=clipping_id)
        clipping_book = clipping_to_delete.book
        
        clipping_to_delete.soft_delete()
        
        # For non-empty books -> previous URL
        if clipping_book.clippings.count():
            return redirect(request.META['HTTP_REFERER'])
    
        # For empty books -> back to main browse page
        return redirect(reverse_lazy('clipping_manager:browse'))
        
class BooksView(ListView):
    template_name = 'clipping_manager/books.html'
    context_object_name = 'books'
    model = Book

    def get_queryset(self):
        return Book.objects.for_user(self.request.user).not_empty()

class UploadMyClippingsFileView(FormView):
    form_class = UploadKindleClippingsForm
    template_name = 'clipping_manager/upload_kindle_clippings_file.html'
    success_url = reverse_lazy('clipping_manager:dashboard')

    def form_valid(self, form):
        if 'clippings_file' not in self.request.FILES:
            messages.add_message(self.request, messages.ERROR, _('Could not process the uploaded file'))
            return super(UploadMyClippingsFileView, self).form_valid(form)

        try:
            clippings_file = EncodedFile(self.request.FILES['clippings_file'], data_encoding='utf-8', errors='ignore')
            clippings_file_content = clippings_file.read()
            clips = kindle_clipping_parser.get_clips_from_text(clippings_file_content)

            # Save the file in db
            language_header = self.request.META.get('HTTP_ACCEPT_LANGUAGE')
            MyClippingsFile.objects.create_file(
                                content=clippings_file_content,
                                language_header=language_header
                            )
        except Exception as e:
            logger.error(f'Error parsing a clippings file.', exc_info=True)
            messages.add_message(
                self.request,
                messages.ERROR,
                _('Couldn\'t process your Clippings. No clippings have been imported. The developer is informed, please try again in a couple of days!')
            )
        else:
            user = self.request.user
            num_books = 0
            num_clippings = 0
            errors = 0
            for book, clippings in clips.items():
                book, created = Book.objects.get_or_create(
                    user=user,
                    title=book,
                )
                if created:
                    num_books += 1
                try:
                    for clip_content in clippings:
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
                    errors += 1
                    logger.error(f'Error importing a clipping.', exc_info=True)

            if errors > 0:
                messages.add_message(
                    self.request,
                    messages.ERROR,
                    _('{num_clippings} clippings could not be imported'.format(num_clippings=errors))
                )

            messages.add_message(
                self.request,
                messages.SUCCESS,
                _('Successfully imported {num_clippings} new clippings from {num_books} books').format(
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

        clippings_file = EncodedFile(
            self.request.FILES['clippings_file'],
            'utf-8',
            errors='ignore',
        )
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
        clipping = Clipping.objects.select_related('book').for_user(self.request.user).not_empty().random()
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

        user_clippings_counts = User.objects.exclude(clippings__isnull=True).values('email').annotate(Count('clippings')).order_by('-clippings__count')
        ctx['user_clippings_tuple'] = user_clippings_counts[:30]
        return ctx


class PersonalStatisticsView(TemplateView):
    template_name = 'clipping_manager/personal_statistics.html'

    def get_statistics(self):
        clips = Clipping.objects.for_user(self.request.user)
        books = Book.objects.for_user(self.request.user).not_empty()

        books_ordered = books.order_by('clippings_count')
        book_most_clips = books_ordered.last()
        if book_most_clips:
            book_most_clips_value = f'{book_most_clips.title} ({book_most_clips.clippings.count()} clippings)'
        else:
            book_most_clips_value = ''

        book_least_clips = books_ordered.first()
        if book_least_clips:
            book_least_clips_value = f'{book_least_clips.title} ({book_least_clips.clippings.count()} clippings)'
        else:
            book_least_clips_value = ''

        book_clippings_counts = books.order_by('-clippings_count').values_list('clippings_count', flat=True)
        if book_clippings_counts:
            mean_clippings_per_book = int(statistics.mean(list(book_clippings_counts)))
        else:
            mean_clippings_per_book = ''

        clip_contents = clips.values_list('content', flat=True)
        clip_number_of_words = [len(clip.split()) for clip in clip_contents]
        clip_number_of_words.sort()
        longest_clip = clip_number_of_words[-1] if len(clip_number_of_words) > 0 else ''
        shortest_clip = clip_number_of_words[0] if len(clip_number_of_words) > 0 else ''

        users_with_more_clips = User.objects.exclude(clippings__isnull=True)\
                                            .annotate(
                                                clippings_count=Count(
                                                    models.Case(models.When(clippings__deleted=False, then=1))
                                                )
                                            )\
                                            .filter(clippings_count__gt=clips.count())\
                                            .count()            
        clips_rank = users_with_more_clips + 1

        # Create dict(user_1: book_count_1, ...)
        books_count_by_user = Counter(Book.objects.not_empty().values_list('user_id', flat=True))
        
        users_with_more_books = len([key for key in books_count_by_user 
                                    if books_count_by_user[key] > books_count_by_user[self.request.user.id]])

        books_rank = users_with_more_books + 1

        mean_word_count = int(statistics.mean(clip_number_of_words)) if len(clip_number_of_words) > 1 else ''

        return [
            {'title': _('Number of clippings'), 'value': clips.count()},
            {'title': _('Number of books'), 'value': books.count()},
            {'title': _('Book with most clippings'), 'value': book_most_clips_value},
            {'title': _('Book with least clippings'), 'value': book_least_clips_value},
            {'title': 'DIVIDER', 'value': ''},  # divider
            {'title': _('Mean clippings per book'), 'value': mean_clippings_per_book},
            {'title': _('Words in longest clipping'), 'value': longest_clip},
            {'title': _('Words in shortest clipping'), 'value': shortest_clip },
            {'title': _('Mean word count'), 'value': mean_word_count},
            # {'title': _('Median word count'), 'value': statistics.median(clip_number_of_words)},
            {'title': 'DIVIDER', 'value': ''},  # divider
            {'title': _('Clippings number rank'), 'value': _('You are #{rank}'.format(rank=clips_rank)) if clips.count() > 0 else ''},
            {'title': _('Books number rank'), 'value': _('You are #{rank}'.format(rank=books_rank)) if clips.count() > 0 else ''},
        ]

    def get_context_data(self, **kwargs):
        ctx = super(PersonalStatisticsView, self).get_context_data(**kwargs)
        ctx['statistics'] = self.get_statistics()
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
