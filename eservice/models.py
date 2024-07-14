from django.db import models

NULLABLE = {'blank': True, 'null': True}


class Client(models.Model):
    """Модель клиента, содержит поля: имя, email, комментарий."""
    name = models.CharField(max_length=255, verbose_name='Ф. И. О.')
    email = models.EmailField(verbose_name='Email')
    comment = models.TextField(verbose_name='Комментарий', **NULLABLE)

    def __str__(self):
        return f"{self.name} - {self.email}"

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'


class Message(models.Model):
    """Модель сообщения, содержит поля: тема, тело"""
    subject = models.CharField(max_length=100, verbose_name="тема", **NULLABLE)
    body = models.TextField(**NULLABLE, verbose_name="тело")

    def __str__(self):
        return f"{self.subject}"

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'


class AttemptsNewsletter(models.Model):
    """Модель рассылки, содержит поля: дата и время последней попытки, статус попытки, ответ почтового сервера."""
    date_time_last_sent = models.DateTimeField(verbose_name="дата и время последней попытки")
    status = models.BooleanField(default=False, verbose_name="статус попытки")
    mail_server_response = models.TextField(verbose_name="ответ почтового сервера", **NULLABLE)

    def __str__(self):
        return f"Рассылка {self.date_time_last_sent} - {self.status}"

    class Meta:
        verbose_name = 'Попытка рассылки'
        verbose_name_plural = 'Попытки рассылки'


class Newsletter(models.Model):
    PERIOD_CHOICES = {
        "DISABLE": 'Отключено',
        "EVERY_DAY": 'Ежедневно',
        "EVERY_WEEK": 'Еженедельно',
        "EVERY_MONTH": 'Ежемесячно',
    }

    STATUS_CHOICES = {
        "CREATED": 'Создана',
        "RUNNED": 'Запущена',
        "COMPLETED": 'Завершена',
    }

    date_time_first_sent = models.DateTimeField(verbose_name="дата и время первой отправки рассылки")
    period = models.CharField(max_length=30, verbose_name="периодичность", choices=PERIOD_CHOICES, default="DISABLE")
    status = models.CharField(max_length=30, verbose_name="статус рассылки", choices=STATUS_CHOICES, default="CREATED")  # пока так
    message = models.ForeignKey(Message, verbose_name="сообщение",
                                on_delete=models.CASCADE,
                                related_name="newsletters")  # Если сообщение удалено, то рассылка тоже удаляется
    clients = models.ManyToManyField(Client, verbose_name="клиенты", related_name="newsletters")

    def __str__(self):
        return f"Рассылка {self.message.subject} - {self.date_time_first_sent} - {self.status}"

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'
