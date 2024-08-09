from django.urls import path
from django.views.decorators.cache import cache_page

from blog.apps import BlogConfig
from blog.views import BlogListView

app_name = BlogConfig.name

urlpatterns = [
    path('blog_list', cache_page(60)(BlogListView.as_view()), name='blog_list'),
]
