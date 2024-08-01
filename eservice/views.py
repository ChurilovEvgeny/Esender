from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView

from eservice.models import Message, Client


# Контроллеры для Client
class ClientCreateView(CreateView):
    model = Client
    fields = ('name', 'email', 'comment',)
    success_url = reverse_lazy('eservice:client_list')


class ClientListView(ListView):
    model = Client
    paginate_by = 8


class ClientDetailView(DetailView):
    model = Client


class ClientUpdateView(UpdateView):
    model = Client
    fields = ('name', 'email', 'comment',)

    def get_success_url(self):
        return reverse('eservice:client_detail', args=[self.kwargs.get('pk')])


def client_delete(request, pk):
    client = get_object_or_404(Client, pk=pk)
    client.delete()
    return redirect('eservice:client_list')


# Контроллеры для Message
class MessageCreateView(CreateView):
    model = Message
    fields = ('subject', 'body')
    success_url = reverse_lazy('eservice:message_list')


class MessageListView(ListView):
    model = Message
    paginate_by = 6


class MessageDetailView(DetailView):
    model = Message

    def post(self, *args, **kwargs):
        message = get_object_or_404(Message, pk=self.kwargs.get('pk'))
        message.delete()
        return redirect('eservice:message_list')


class MessageUpdateView(UpdateView):
    model = Message
    fields = ('subject', 'body')

    def get_success_url(self):
        return reverse('eservice:message_detail', args=[self.kwargs.get('pk')])


def message_delete(request, pk):
    message = get_object_or_404(Message, pk=pk)
    message.delete()
    return redirect('eservice:message_list')
