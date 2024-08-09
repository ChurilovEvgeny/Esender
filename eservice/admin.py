from django.contrib import admin

from eservice.models import Client, Message, AttemptsNewsletter, Newsletter


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'comment')
    list_filter = ('name', 'email')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'body')
    list_filter = ('subject',)


@admin.register(AttemptsNewsletter)
class AttemptsNewsletterAdmin(admin.ModelAdmin):
    list_display = ('date_time_last_sent', 'status', 'mail_server_response')
    list_filter = ('status',)


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    # возможно стоит решить проблема с 'clients'
    list_display = ('date_time_first_sent', 'period', 'status', 'message',)
    list_filter = ('status', 'period')

    def get_readonly_fields(self, request, obj=None):
        # Для супер доступны полностью настройки пользователя
        # Для менеджера доступны только поля is_active
        # Во всех остальных случаях все поля недоступны.
        if request.user.is_superuser:
            return super().get_readonly_fields(request, obj=obj)
        if request.user.groups.filter(name='Manager').exists():
            # Получаем список всех полей и исключаем period
            readonly_fields = list(
                set(
                    [field.name for field in self.opts.local_fields] +
                    [field.name for field in self.opts.local_many_to_many]
                ))

            if 'period' in readonly_fields:
                readonly_fields.remove('period')

            return readonly_fields
        return tuple()
