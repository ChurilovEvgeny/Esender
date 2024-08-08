from django.contrib import admin

from users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    limited_fields = ('is_active',)

    def get_fields(self, request, obj=None):
        # Для супер доступны полностью настройки пользователя
        # Для менеджера доступны только поля is_active
        # Во всех остальных случаях все поля недоступны.
        if request.user.is_superuser:
            return super().get_fields(request, obj=obj)
        if request.user.groups.filter(name='Manager').exists():
            return self.limited_fields
        return tuple()
