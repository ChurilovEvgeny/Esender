from django.urls import path

from eservice.apps import EserviceConfig
from eservice.views import MessageListView, MessageCreateView, MessageUpdateView, MessageDetailView, message_delete, \
    ClientListView, ClientDetailView, ClientCreateView, ClientUpdateView, client_delete

app_name = EserviceConfig.name

urlpatterns = [
    path('', MessageListView.as_view(), name='message_list'),
    path('message_create/', MessageCreateView.as_view(), name='message_create'),
    path('message_form/', MessageCreateView.as_view(), name='message_create'),
    path('message_form/<int:pk>', MessageUpdateView.as_view(), name='message_update'),
    path('message_detail/<int:pk>', MessageDetailView.as_view(), name='message_detail'),
    path('message_delete/<int:pk>', message_delete, name='message_delete'),

    path('client_list/', ClientListView.as_view(), name='client_list'),
    path('client_form/', ClientCreateView.as_view(), name='client_create'),
    path('client_form/<int:pk>', ClientUpdateView.as_view(), name='client_update'),
    path('client_detail/<int:pk>', ClientDetailView.as_view(), name='client_detail'),
    path('client_delete/<int:pk>', client_delete, name='client_delete'),
]
