import datetime

from dateutil.relativedelta import relativedelta
from django.db import models
from django.db.models import Q, QuerySet
from django.utils import timezone

NULLABLE = {"blank": True, "null": True}


class Client(models.Model):
    """Модель клиента, содержит поля: имя, email, комментарий."""

    name = models.CharField(max_length=255, verbose_name="Ф. И. О.")
    email = models.EmailField(verbose_name="Email")
    comment = models.TextField(verbose_name="Комментарий", **NULLABLE)

    def __str__(self):
        return f"{self.name} - {self.email}"

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"


class Message(models.Model):
    """Модель сообщения, содержит поля: тема, тело"""

    subject = models.CharField(max_length=100, verbose_name="тема", **NULLABLE)
    body = models.TextField(**NULLABLE, verbose_name="тело")

    def __str__(self):
        return f"{self.subject}"

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"


class Newsletter(models.Model):
    PERIOD_DISABLE = "DISABLE"
    PERIOD_EVERY_DAY = "EVERY_DAY"
    PERIOD_EVERY_WEEK = "EVERY_WEEK"
    PERIOD_EVERY_MONTH = "EVERY_MONTH"

    STATUS_CREATED = "CREATED"
    STATUS_LAUNCHED = "LAUNCHED"
    STATUS_COMPLETED = "COMPLETED"

    PERIOD_CHOICES = {
        PERIOD_DISABLE: "Отключено",
        PERIOD_EVERY_DAY: "Ежедневно",
        PERIOD_EVERY_WEEK: "Еженедельно",
        PERIOD_EVERY_MONTH: "Ежемесячно",
    }

    STATUS_CHOICES = {
        STATUS_CREATED: "Создана",
        STATUS_LAUNCHED: "Запущена",
        STATUS_COMPLETED: "Завершена",
    }

    date_time_first_sent = models.DateTimeField(
        verbose_name="дата и время первой отправки рассылки"
    )
    date_time_last_sent = models.DateTimeField(
        verbose_name="дата и время последней отправки рассылки", blank=True, null=True
    )

    period = models.CharField(
        max_length=30,
        verbose_name="периодичность",
        choices=PERIOD_CHOICES,
        default="DISABLE",
    )
    status = models.CharField(
        max_length=30,
        verbose_name="статус рассылки",
        choices=STATUS_CHOICES,
        default=STATUS_CREATED,
    )  # пока так
    message = models.ForeignKey(
        Message,
        verbose_name="сообщение",
        on_delete=models.CASCADE,
        related_name="newsletters",
    )  # Если сообщение удалено, то рассылка тоже удаляется
    clients = models.ManyToManyField(
        Client, verbose_name="клиенты", related_name="newsletters"
    )

    # заполняется программно в алгоритме, по умолчанию date_time_first_sent
    date_time_next_sent = models.DateTimeField(
        verbose_name="дата и время следующей рассылки", blank=True, null=True
    )

    @classmethod
    def get_newsletters_ready_to_sent(cls) -> QuerySet:
        # (CREATED or RUNNED) and (date_time_next_sent <= now_time)
        # Если создана или запущена и если текущая дата/время больше или равно
        # дате/времени следующей рассылки, то выбрать
        # Следует использовать timezone.now(), а не datetime.now(), так как django ругается
        now_time = timezone.now().replace(
            second=0, microsecond=0
        )  # Сбрасываем секунды для корректного сравнения
        print(now_time)

        query = Q(status=cls.STATUS_CREATED)
        query.add(Q(status=cls.STATUS_LAUNCHED), Q.OR)
        query.add(Q(date_time_next_sent__lte=now_time), Q.AND)

        newsletters = cls.objects.filter(query)
        return newsletters

    def set_next_sent_datetime(self):

        def get_next_day_date(date_time_start_sent, now_time):
            # К дате/времени начала рассылки прибавляются недостающие дни к текущей дате
            # плюс один день на следующую рассылку
            if now_time > date_time_start_sent:
                next_date_time_diff = (now_time - date_time_start_sent).days + 1
                delta = datetime.timedelta(days=next_date_time_diff)
                return date_time_start_sent + delta
            else:
                return date_time_start_sent

        def get_next_week_date(date_time_start_sent, now_time):
            # К дате/времени начала рассылки прибавляются недостающие дни к текущей дате
            # плюс разница до следующей недели на следующую рассылку
            if now_time > date_time_start_sent:
                now_start_delta = (now_time - date_time_start_sent).days
                delta = now_start_delta + (7 - now_start_delta % 7)
                return date_time_start_sent + datetime.timedelta(days=delta)
            else:
                return date_time_start_sent

        def get_next_month_date(date_time_start_sent, now_time):
            # Библиотечная функция при добавлении к месяцу учитывает количество дней, к примеру
            # дата начала рассылки 31 января, но следующая дата выставится исходя из количества дней в месяце,
            # то есть в феврале будет 28 или 29 февраля, а в апреле будет 30 апреля, но в марте будет 31 марта
            if now_time > date_time_start_sent:
                month_count = relativedelta(now_time, date_time_start_sent).months + 1
                return date_time_start_sent + relativedelta(months=month_count)
            else:
                return date_time_start_sent

        date_time_start_sent = self.date_time_first_sent.replace(
            second=0, microsecond=0
        )
        now_time = timezone.now().replace(second=0, microsecond=0)

        match self.period:
            case self.PERIOD_EVERY_DAY:
                # self.date_time_next_sent = get_next_day_date(date_time_start_sent, now_time)
                delta = timezone.timedelta(minutes=2)
                self.date_time_next_sent = now_time + delta

            case self.PERIOD_EVERY_WEEK:
                self.date_time_next_sent = get_next_week_date(
                    date_time_start_sent, now_time
                )

            case self.PERIOD_EVERY_MONTH:
                self.date_time_next_sent = get_next_month_date(
                    date_time_start_sent, now_time
                )

            case _:
                pass

        self.date_time_next_sent = self.date_time_next_sent.replace(
            second=0, microsecond=0
        )
        self.save()

    def refresh_status(self):
        new_status = self.make_status(
            self.date_time_first_sent, self.date_time_last_sent
        )
        if self.status != new_status:
            self.status = new_status
            self.save()

    @classmethod
    def make_status(cls, date_time_first_sent, date_time_last_sent):
        date_time_first_sent = date_time_first_sent.replace(second=0, microsecond=0)
        if date_time_last_sent:
            date_time_last_sent = date_time_last_sent.replace(second=0, microsecond=0)
        now_time = timezone.now().replace(second=0, microsecond=0)

        if date_time_last_sent and now_time > date_time_last_sent:
            return cls.STATUS_COMPLETED
        elif now_time >= date_time_first_sent:
            return cls.STATUS_LAUNCHED

        return cls.STATUS_CREATED

    def __str__(self):
        return f"Рассылка {self.message.subject}; Начало: {self.date_time_first_sent}; Окончание: {self.date_time_last_sent}; След.: {self.date_time_next_sent}; {self.period}; {self.status}"

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"


class AttemptsNewsletter(models.Model):
    """Модель рассылки, содержит поля: дата и время последней попытки, статус попытки, ответ почтового сервера."""

    newsletter = models.ForeignKey(
        Newsletter,
        verbose_name="рассылка",
        on_delete=models.CASCADE,
        related_name="attempts_newsletter",
        blank=True,
        null=True,
    )
    date_time_last_sent = models.DateTimeField(
        verbose_name="дата и время последней попытки"
    )
    status = models.BooleanField(default=False, verbose_name="статус попытки")
    mail_server_response = models.TextField(
        verbose_name="ответ почтового сервера", **NULLABLE
    )

    def __str__(self):
        return f"Рассылка: {self.newsletter}; {self.date_time_last_sent}; {self.status}"

    class Meta:
        verbose_name = "Попытка рассылки"
        verbose_name_plural = "Попытки рассылки"
