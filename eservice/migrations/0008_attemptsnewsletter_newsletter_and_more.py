# Generated by Django 5.0.7 on 2024-08-04 13:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eservice', '0007_newsletter_date_time_next_sent'),
    ]

    operations = [
        migrations.AddField(
            model_name='attemptsnewsletter',
            name='newsletter',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='attempts_newsletter', to='eservice.newsletter', verbose_name='рассылка'),
        ),
        migrations.AlterField(
            model_name='newsletter',
            name='status',
            field=models.CharField(choices=[('CREATED', 'Создана'), ('LAUNCHED', 'Запущена'), ('COMPLETED', 'Завершена')], default='CREATED', max_length=30, verbose_name='статус рассылки'),
        ),
    ]
