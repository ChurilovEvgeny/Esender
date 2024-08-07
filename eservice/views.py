from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import loader
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, DetailView, UpdateView

from blog.models import Blog
from eservice.forms import NewsletterForm, NewsletterModeratorForm
from eservice.models import Message, Client, Newsletter, AttemptsNewsletter
from eservice.views_services import AutoOwnerMixin, delete, ObjectsListAccessMixin, ObjectDetailAccessMixin, \
    is_super_or_owner, CustomLoginRequiredMixin


# Контроллеры для Client
class ClientCreateView(LoginRequiredMixin, AutoOwnerMixin, CreateView):
    model = Client
    fields = ('name', 'email', 'comment',)
    success_url = reverse_lazy('eservice:client_list')
    login_url = reverse_lazy('users:login')


class ClientListView(LoginRequiredMixin, ObjectsListAccessMixin, ListView):
    model = Client
    paginate_by = 8
    login_url = reverse_lazy('users:login')


class ClientDetailView(ObjectDetailAccessMixin, DetailView):
    model = Client


class ClientUpdateView(CustomLoginRequiredMixin, UpdateView):
    model = Client
    fields = ('name', 'email', 'comment',)
    login_url = reverse_lazy('users:login')

    def form_valid(self, form):
        if form.is_valid():
            new_client = form.save()
            if is_super_or_owner(self.request.user, new_client.owner):
                new_client.save()
            else:
                return redirect('users:login')

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('eservice:client_detail', args=[self.kwargs.get('pk')])


@login_required(login_url=reverse_lazy('users:login'))
def client_delete(request, pk):
    return delete(request, pk)


# Контроллеры для Message
class MessageCreateView(LoginRequiredMixin, AutoOwnerMixin, CreateView):
    model = Message
    fields = ('subject', 'body')
    success_url = reverse_lazy('eservice:message_list')
    login_url = reverse_lazy('users:login')


class MessageListView(LoginRequiredMixin, ObjectsListAccessMixin, ListView):
    model = Message
    paginate_by = 6
    login_url = reverse_lazy('users:login')


class MessageDetailView(ObjectDetailAccessMixin, DetailView):
    model = Message


class MessageUpdateView(CustomLoginRequiredMixin, UpdateView):
    model = Message
    fields = ('subject', 'body')

    def form_valid(self, form):
        if form.is_valid():
            new_message = form.save()
            if is_super_or_owner(self.request.user, new_message.owner):
                new_message.save()
            else:
                raise PermissionDenied

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('eservice:message_detail', args=[self.kwargs.get('pk')])


@login_required(login_url=reverse_lazy('users:login'))
def message_delete(request, pk):
    return delete(request, pk)


# Контроллеры для Newsletter
class NewsletterCreateView(LoginRequiredMixin, AutoOwnerMixin, CreateView):
    model = Newsletter
    form_class = NewsletterForm
    success_url = reverse_lazy('eservice:newsletter_list')
    login_url = reverse_lazy('users:login')

    def form_valid(self, form):
        if form.is_valid():
            new_newsletter = form.save()
            new_newsletter.set_next_sent_datetime()
            new_newsletter.refresh_status()
            new_newsletter.save()
        return super().form_valid(form)


class NewsletterListView(LoginRequiredMixin, ObjectsListAccessMixin, ListView):
    model = Newsletter
    paginate_by = 16
    login_url = reverse_lazy('users:login')


class NewsletterDetailView(ObjectDetailAccessMixin, DetailView):
    model = Newsletter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        clients = context["object"].clients.get_queryset()[:100]
        clients_list = [str(item) for item in clients]
        context["object"].clients_list = clients_list
        return context


class NewsletterUpdateView(LoginRequiredMixin, UpdateView):
    model = Newsletter
    form_class = NewsletterForm
    login_url = reverse_lazy('users:login')

    def get_form_class(self):
        user = self.request.user
        if user.is_superuser or user == self.object.owner:
            return NewsletterForm
        elif user.has_perm("eservice.manager"):
            return NewsletterModeratorForm

        raise PermissionDenied

    def get_success_url(self):
        return reverse('eservice:newsletter_detail', args=[self.kwargs.get('pk')])

    def form_valid(self, form):
        if form.is_valid():
            new_newsletter = form.save()
            if type(form) is NewsletterForm:
                if is_super_or_owner(self.request.user, new_newsletter.owner):
                    new_newsletter.set_next_sent_datetime()
                    new_newsletter.refresh_status()
                    new_newsletter.save()
                else:
                    raise PermissionDenied
            elif type(form) is NewsletterModeratorForm:
                if self.request.user.has_perm('eservice.manager'):
                    new_newsletter.save()
                else:
                    raise PermissionDenied
            else:
                raise PermissionDenied

        return super().form_valid(form)


@login_required(login_url=reverse_lazy('users:login'))
def newsletter_delete(request, pk):
    return delete(request, pk)


class AttemptsNewsletterListView(LoginRequiredMixin, ObjectsListAccessMixin, ListView):
    model = AttemptsNewsletter
    paginate_by = 10
    login_url = reverse_lazy('users:login')


def index(request):
    context = {}
    context['total_newsletter_count'] = Newsletter.get_total_newsletters()
    context['active_newsletter_count'] = Newsletter.get_total_active_newsletters()
    context['unique_clients_count'] = Client.get_unique_clients_count()
    context['blogs'] = Blog.get_3_random_blogs()
    template = loader.get_template('eservice/index.html')
    context = {
        'context': context,
    }
    return HttpResponse(template.render(context, request))
