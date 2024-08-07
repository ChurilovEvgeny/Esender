from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, DetailView, UpdateView

from eservice.forms import NewsletterForm, NewsletterModeratorForm
from eservice.models import Message, Client, Newsletter, AttemptsNewsletter


def has_view_all_list_perms(current_user):
    """Получать весь список объектов может супер или менеджер"""
    return current_user.is_superuser or current_user.has_perm('eservice.manager')


def has_update_perms(current_user, object_owner):
    return current_user.is_superuser or current_user == object_owner


def has_delete_perms(current_user, object_owner):
    """Непосредственно перед удалением объекта дополнительная проверка на валидного пользователя"""
    return current_user.is_superuser or current_user == object_owner


class CreateViewWithAutoOwner(LoginRequiredMixin, CreateView):
    login_url = reverse_lazy('users:login')

    def __fill_owner(self, form):
        """Функция добавляет значение в поле owner"""
        form_obj = form.save()
        user = self.request.user
        form_obj.owner = user
        form_obj.save()

    def form_valid(self, form):
        self.__fill_owner(form)
        return super().form_valid(form)


class ListViewOwnerItems(LoginRequiredMixin, ListView):
    login_url = reverse_lazy('users:login')

    def get_queryset(self):
        user = self.request.user
        # Если текущий пользователь супер или же менеджер, то возвращаем весь список
        if has_view_all_list_perms(user):
            return super().get_queryset()
        return self.model.objects.filter(owner=user)


class DetailViewAccessControl(DetailView):
    def get_object(self, queryset=None):
        if has_view_all_list_perms(self.request.user):
            return super().get_object(queryset)
        return get_object_or_404(self.model, owner=self.request.user)


# Контроллеры для Client
class ClientCreateView(CreateViewWithAutoOwner):
    model = Client
    fields = ('name', 'email', 'comment',)
    success_url = reverse_lazy('eservice:client_list')


class ClientListView(ListViewOwnerItems):
    model = Client
    paginate_by = 8


class ClientDetailView(DetailViewAccessControl):
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
    if has_delete_perms(request.user, client.owner):
        client.delete()
    return redirect('eservice:client_list')


# Контроллеры для Message
class MessageCreateView(CreateViewWithAutoOwner):
    model = Message
    fields = ('subject', 'body')
    success_url = reverse_lazy('eservice:message_list')


class MessageListView(ListViewOwnerItems):
    model = Message
    paginate_by = 6


class MessageDetailView(DetailViewAccessControl):
    model = Message


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = Message
    fields = ('subject', 'body')
    login_url = reverse_lazy('users:login')

    def get_success_url(self):
        return reverse('eservice:message_detail', args=[self.kwargs.get('pk')])


@login_required(login_url=reverse_lazy('users:login'))
def message_delete(request, pk):
    message = get_object_or_404(Message, pk=pk)
    if has_delete_perms(request.user, message.owner):
        message.delete()
    return redirect('eservice:message_list')


# Контроллеры для Newsletter
class NewsletterCreateView(CreateViewWithAutoOwner):
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


class NewsletterListView(ListViewOwnerItems):
    model = Newsletter
    paginate_by = 16


class NewsletterDetailView(DetailView):
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
                if self.request.user.is_superuser or self.request.user == new_newsletter.owner:
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
    newsletter = get_object_or_404(Newsletter, pk=pk)
    if has_delete_perms(request.user, newsletter.owner):
        newsletter.delete()
    return redirect('eservice:newsletter_list')


class AttemptsNewsletterListView(ListViewOwnerItems):
    model = AttemptsNewsletter
    paginate_by = 10
