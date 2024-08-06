import asyncio
import pathlib
import uuid
from smtplib import SMTPAuthenticationError

from django.core.mail import send_mail

from config.settings import EMAIL_HOST_USER


def generate_filename_user_avatar(instance, filename):
    return generate_filename(instance, filename, 'users')


def generate_filename_product(instance, filename):
    return generate_filename(instance, filename, 'products')


def generate_filename_blog(instance, filename):
    return generate_filename(instance, filename, 'blog')


def generate_filename(instance, filename, subdir):
    return pathlib.Path(subdir) / f"{uuid.uuid4().hex}.{filename.split('.')[-1]}"


def send_mail_async(subject, message, recipient_list):
    async def run_async():
        try:
            send_mail(
                subject,
                message,
                EMAIL_HOST_USER,
                recipient_list,
                fail_silently=False,
            )
        except SMTPAuthenticationError:
            print('Не удалось авторизоваться на почте')
        except Exception as e:
            print("Ошибка отправки сообщения' + e")

    asyncio.run(run_async())
