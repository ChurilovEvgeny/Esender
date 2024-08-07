from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, DetailView, UpdateView

from eservice.forms import NewsletterForm
from eservice.models import Message, Client, Newsletter, AttemptsNewsletter


# Контроллеры для Client
class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    fields = ('name', 'email', 'comment',)
    success_url = reverse_lazy('eservice:client_list')
    login_url = reverse_lazy('users:login')


class ClientListView(ListView):
    model = Client
    paginate_by = 8


class ClientDetailView(DetailView):
    model = Client


class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    fields = ('name', 'email', 'comment',)
    login_url = reverse_lazy('users:login')

    def get_success_url(self):
        return reverse('eservice:client_detail', args=[self.kwargs.get('pk')])


@login_required(login_url=reverse_lazy('users:login'))
def client_delete(request, pk):
    client = get_object_or_404(Client, pk=pk)
    client.delete()
    return redirect('eservice:client_list')


# Контроллеры для Message
class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    fields = ('subject', 'body')
    success_url = reverse_lazy('eservice:message_list')
    login_url = reverse_lazy('users:login')


class MessageListView(ListView):
    model = Message
    paginate_by = 6


class MessageDetailView(DetailView):
    model = Message

    def post(self, *args, **kwargs):
        message = get_object_or_404(Message, pk=self.kwargs.get('pk'))
        message.delete()
        return redirect('eservice:message_list')


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = Message
    fields = ('subject', 'body')
    login_url = reverse_lazy('users:login')

    def get_success_url(self):
        return reverse('eservice:message_detail', args=[self.kwargs.get('pk')])


@login_required(login_url=reverse_lazy('users:login'))
def message_delete(request, pk):
    message = get_object_or_404(Message, pk=pk)
    message.delete()
    return redirect('eservice:message_list')


# Контроллеры для Newsletter
class NewsletterCreateView(LoginRequiredMixin, CreateView):
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


class NewsletterListView(ListView):
    model = Newsletter
    paginate_by = 16


class NewsletterDetailView(DetailView):
    model = Newsletter

    def post(self, *args, **kwargs):
        message = get_object_or_404(Newsletter, pk=self.kwargs.get('pk'))
        message.delete()
        return redirect('eservice:newsletter_list')

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

    def get_success_url(self):
        return reverse('eservice:newsletter_detail', args=[self.kwargs.get('pk')])

    def form_valid(self, form):
        if form.is_valid():
            new_newsletter = form.save()
            new_newsletter.set_next_sent_datetime()
            new_newsletter.refresh_status()
            new_newsletter.save()
        return super().form_valid(form)


@login_required(login_url=reverse_lazy('users:login'))
def newsletter_delete(request, pk):
    message = get_object_or_404(Newsletter, pk=pk)
    message.delete()
    return redirect('eservice:newsletter_list')


class AttemptsNewsletterListView(ListView):
    model = AttemptsNewsletter
    paginate_by = 10
