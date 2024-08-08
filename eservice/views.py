from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.template import loader
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, DetailView, UpdateView

from blog.models import Blog
from eservice.forms import NewsletterForm, NewsletterModeratorForm
from eservice.models import Message, Client, Newsletter, AttemptsNewsletter
from eservice.views_services import AutoOwnerMixin, delete, ObjectsListAccessMixin, ObjectDetailAccessMixin, \
    is_super_or_owner, CustomLoginRequiredMixin, CustomLoginRequiredMixin2, is_user_manager, CustomLoginRequiredMixin3


# Контроллеры для Client
class ClientCreateView(CustomLoginRequiredMixin3, AutoOwnerMixin, CreateView):
    model = Client
    fields = ('name', 'email', 'comment',)
    success_url = reverse_lazy('eservice:client_list')


class ClientListView(CustomLoginRequiredMixin3, ObjectsListAccessMixin, ListView):
    model = Client
    paginate_by = 8


class ClientDetailView(ObjectDetailAccessMixin, DetailView):
    model = Client


class ClientUpdateView(CustomLoginRequiredMixin, UpdateView):
    model = Client
    fields = ('name', 'email', 'comment',)

    def get_success_url(self):
        return reverse('eservice:client_detail', args=[self.kwargs.get('pk')])


@login_required
def client_delete(request, pk):
    return delete(Client, request, pk)


# Контроллеры для Message
class MessageCreateView(CustomLoginRequiredMixin3, AutoOwnerMixin, CreateView):
    model = Message
    fields = ('subject', 'body')
    success_url = reverse_lazy('eservice:message_list')


class MessageListView(CustomLoginRequiredMixin3, ObjectsListAccessMixin, ListView):
    model = Message
    paginate_by = 6


class MessageDetailView(ObjectDetailAccessMixin, DetailView):
    model = Message


class MessageUpdateView(CustomLoginRequiredMixin, UpdateView):
    model = Message
    fields = ('subject', 'body')

    def get_success_url(self):
        return reverse('eservice:message_detail', args=[self.kwargs.get('pk')])


@login_required
def message_delete(request, pk):
    return delete(Message, request, pk)


# Контроллеры для Newsletter
class NewsletterCreateView(CustomLoginRequiredMixin3, AutoOwnerMixin, CreateView):
    model = Newsletter
    form_class = NewsletterForm
    success_url = reverse_lazy('eservice:newsletter_list')

    def form_valid(self, form):
        if form.is_valid():
            new_newsletter = form.save()
            new_newsletter.set_next_sent_datetime()
            new_newsletter.refresh_status()
            new_newsletter.save()
        return super().form_valid(form)


class NewsletterListView(CustomLoginRequiredMixin3, ObjectsListAccessMixin, ListView):
    model = Newsletter
    paginate_by = 16


class NewsletterDetailView(ObjectDetailAccessMixin, DetailView):
    model = Newsletter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        clients = context["object"].clients.get_queryset()[:100]
        clients_list = [str(item) for item in clients]
        context["object"].clients_list = clients_list
        return context


class NewsletterUpdateView(CustomLoginRequiredMixin2, UpdateView):
    model = Newsletter
    form_class = NewsletterForm

    def get_form_class(self):
        user = self.request.user
        if is_super_or_owner(current_user=user, object_owner=self.object.owner):
            return NewsletterForm
        elif is_user_manager(user):
            return NewsletterModeratorForm

        raise PermissionDenied

    def get_success_url(self):
        return reverse('eservice:newsletter_detail', args=[self.kwargs.get('pk')])

    def form_valid(self, form):
        if form.is_valid():
            new_newsletter = form.save()
            if type(form) is NewsletterForm:
                new_newsletter.set_next_sent_datetime()
                new_newsletter.refresh_status()
                new_newsletter.save()
            elif type(form) is NewsletterModeratorForm:
                new_newsletter.save()
            else:
                raise PermissionDenied

        return super().form_valid(form)


@login_required
def newsletter_delete(request, pk):
    return delete(Newsletter, request, pk)


class AttemptsNewsletterListView(CustomLoginRequiredMixin3, ObjectsListAccessMixin, ListView):
    model = AttemptsNewsletter
    paginate_by = 10


def index(request):
    data = {
        'total_newsletter_count': Newsletter.get_total_newsletters(),
        'active_newsletter_count': Newsletter.get_total_active_newsletters(),
        'unique_clients_count': Client.get_unique_clients_count(),
        'blogs': Blog.get_3_random_blogs()
    }
    template = loader.get_template('eservice/index.html')
    context = {
        'context': data,
    }
    return HttpResponse(template.render(context, request))
