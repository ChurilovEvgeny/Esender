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
