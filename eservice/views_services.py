from django.contrib.auth.mixins import AccessMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy

from eservice.models import Message


def is_super_or_manager(current_user):
    """Получать весь список объектов может супер или менеджер"""
    return current_user.is_superuser or current_user.has_perm('eservice.manager')


def is_super_or_owner(current_user, object_owner):
    """Непосредственно перед удалением объекта дополнительная проверка на валидного пользователя"""
    return current_user.is_superuser or current_user == object_owner


def is_super_or_owner_or_manger(current_user, object_owner):
    return is_super_or_manager(current_user) or is_super_or_owner(current_user, object_owner)


class CustomLoginRequiredMixin(AccessMixin):
    """
    Миксин для проверки на авторизацию, как реализовано в LoginRequiredMixin,
    и проверки, что пользователь супер или же владелец объекта
    """
    login_url = reverse_lazy('users:login')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        obj = get_object_or_404(self.model, pk=kwargs.get('pk', 0))
        if not is_super_or_owner(request.user, obj.owner):
            return self.handle_no_permission()

        return super().dispatch(request, *args, **kwargs)

    def handle_no_permission(self):
        return redirect(self.login_url)


class AutoOwnerMixin:
    """
    Миксин для автозаполнения владельца объекта
    """

    def __fill_owner(self, form):
        """Функция добавляет значение в поле owner"""
        form_obj = form.save()
        user = self.request.user
        form_obj.owner = user
        form_obj.save()

    def form_valid(self, form):
        self.__fill_owner(form)
        return super().form_valid(form)


class ObjectsListAccessMixin:
    """
    Миксин для предоставления полного списка объектов для супера и менеджера;
    или ограниченного списка, принадлежащего текущему пользователю
    """

    def get_queryset(self):
        user = self.request.user
        # Если текущий пользователь супер или же менеджер, то возвращаем весь список
        if is_super_or_manager(user):
            return super().get_queryset()
        return self.model.objects.filter(owner=user)


class ObjectDetailAccessMixin(UserPassesTestMixin):
    login_url = reverse_lazy('users:login')

    def get_object(self, queryset=None):
        return super().get_object(queryset)

    def test_func(self):
        obj = super().get_object(None)
        return is_super_or_owner_or_manger(self.request.user, obj.owner)

    def handle_no_permission(self):
        return redirect(self.login_url)


def delete(request, pk):
    """
    Удаление объекта, проверяя его владельца с помощью is_super_or_owner.
    Если удаляется объект, перенаправляет на страницу списка рассылок.
    Если не удаляется, перенаправляет на страницу авторизации.
    :param request: HttpRequest
    :param pk: int
    :return: HttpResponse
    """
    obj = get_object_or_404(Message, pk=pk)
    if is_super_or_owner(request.user, obj.owner):
        obj.delete()
        return redirect('eservice:newsletter_list')

    return redirect(reverse('users:login'))
