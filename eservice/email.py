import threading
from smtplib import SMTPAuthenticationError, SMTPException

from django.core.mail import send_mail
from django.utils import timezone

from config.settings import EMAIL_HOST_USER
from eservice.models import Newsletter


class EmailThread(threading.Thread):
    def __init__(self, subject, html_content, recipient_list):
        self.subject = subject
        self.recipient_list = recipient_list
        self.html_content = html_content
        self.operation_completed = False
        self.operation_text = ""
        threading.Thread.__init__(self)

    def run(self):
        try:
            send_mail(
                self.subject,
                self.html_content,
                EMAIL_HOST_USER,
                self.recipient_list,
                fail_silently=False,
            )
            self.operation_completed = True
        except SMTPAuthenticationError:
            self.operation_text = "Не удалось авторизоваться на почте"
        except SMTPException as e:
            self.operation_text = "SMTPException " + str(e)
        except Exception as e:
            self.operation_text = "Exception " + str(e)


def send_mail_async(subject, html_content, recipient_list):
    EmailThread(subject, html_content, recipient_list).start()


def send(newsletter: Newsletter):
    send_time = timezone.now()

    clients = newsletter.clients.get_queryset()

    email_threads = []
    for client in clients:
        email_threads.append(EmailThread(newsletter.message.subject, newsletter.message.body, [client.email]))

    print("Send started")
    [email_thread.start() for email_thread in email_threads]
    [email_thread.join() for email_thread in email_threads]
    print("Send competed")

    res = make_operation_result(email_threads)
    print(res)
    return send_time, res[0], res[1]
    # send_mail_async(newsletter.message.subject, newsletter.message.body, [client.email])


def make_operation_result(email_threads: list[EmailThread]) -> tuple[bool, str]:
    # По тз сказано, что у одной попытки рассылки должна быть одна запись в БД, без привязки к количеству клиентов
    # Поэтому сделан такой алгоритм

    # Если все в ошибках, то берем сообщение первого
    is_all_in_error = all([not email_thread.operation_completed for email_thread in email_threads])
    if is_all_in_error:
        return False, email_threads[0].operation_text
    # Если хотя-бы один без ошибки, то записываем успешную отправку
    else:
        return True, "OK"
