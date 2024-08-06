from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from users.apps import UsersConfig
from users.views import RegisterView, ProfileView, email_verification, ProfilePasswordRestoreView, \
    password_restore_success, user_create_success

app_name = UsersConfig.name

urlpatterns = [
    path('', LoginView.as_view(template_name='users/user_login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('confirm/<str:token>/', email_verification, name='confirm'),
    path('password_restore/', ProfilePasswordRestoreView.as_view(), name='password_restore'),
    path('password_restore_success/', password_restore_success, name='password_restore_success'),
    path('user_create_success/', user_create_success, name='user_create_success'),
]
