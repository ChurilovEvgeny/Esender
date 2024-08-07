from django.db import models

from utils.utils import generate_filename_blog


class Blog(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    content = models.TextField(verbose_name="Cодержимое статьи")
    image = models.ImageField(
        upload_to=generate_filename_blog,
        verbose_name="Изображение",
        blank=True,
        null=True,
    )
    views_count = models.PositiveIntegerField(
        default=0, verbose_name="Количество просмотров"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата публикации")

    def __str__(self):
        return f"{self.title}"

    @classmethod
    def get_3_random_blogs(cls):
        blogs = cls.objects.order_by("?")[:3]
        [blog.update_views() for blog in blogs]
        return blogs

    def update_views(self):
        self.views_count += 1
        self.save()


    class Meta:
        verbose_name = "Блог"
        verbose_name_plural = "Блоги"
        ordering = ["title", "created_at", "views_count"]

        permissions = [
            ("content_manager", "Контент-менеджер"),
        ]
