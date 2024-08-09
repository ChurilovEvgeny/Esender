
import secrets

from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, UpdateView

from users.forms import UserRegisterForm, UserProfileForm, ProfilePasswordRestoreForm
from users.models import User
from utils.utils import send_mail_async


class RegisterView(CreateView):
    model = User
    form_class = UserRegisterForm
    template_name = 'users/user_register.html'
    success_url = reverse_lazy('users:user_create_success')

    def form_valid(self, form):
        user = form.save()
        user.is_active = False
        token = secrets.token_hex(32)
        user.token = token
        host = self.request.get_host()
        url = f"http://{host}/users/confirm/{token}/"
        send_mail_async("Подтверждение почты", f"Для подтверждения вашей почты перейдите по ссылке ниже!\n{url}",
                        [user.email])
        user.save()
        return super().form_valid(form)


class ProfileView(UpdateView):
    model = User
    form_class = UserProfileForm
    success_url = reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        return self.request.user


class ProfilePasswordRestoreView(CreateView):
    model = User
    form_class = ProfilePasswordRestoreForm
    template_name = 'users/user_password_restore.html'
    success_url = reverse_lazy('users:password_restore_success')

    def form_valid(self, form):
        # Если from valid, то намеренно не вызываем родительский метод, чтобы не было попытки сохранения в БД!!!
        email = form.cleaned_data['email']
        user = get_object_or_404(User, email=email)
        password = User.objects.make_random_password()
        user.set_password(password)
        user.save(update_fields=['password'])

        send_mail_async("Новый пароль", f"Ваш новый пароль!\n{password}",
                        [user.email])

        return redirect(self.success_url)


def email_verification(request, token):
    user = get_object_or_404(User, token=token)
    user.is_active = True
    user.save()
    return redirect(reverse('users:login'))


def password_restore_success(request):
    return render(request, 'users/user_password_restore_success.html')


def user_create_success(request):
    return render(request, 'users/user_create_success.html')
