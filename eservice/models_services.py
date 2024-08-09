from django.core.cache import cache

from config import settings


def get_cached_newsletters_count(cls):
    if not settings.CACHE_ENABLED:
        return cls.objects.all().count()

    key = 'newsletters_count'
    newsletters_count = cache.get(key)
    if newsletters_count is None:
        newsletters_count = cls.objects.all().count()
        cache.set(key, newsletters_count)

    return newsletters_count


def get_cached_total_active_newsletters(cls):
    if not settings.CACHE_ENABLED:
        return cls.objects.filter(status=cls.STATUS_LAUNCHED).count()

    key = 'active_newsletters'
    active_newsletters = cache.get(key)
    if active_newsletters is None:
        active_newsletters = cls.objects.filter(status=cls.STATUS_LAUNCHED).count()
        cache.set(key, active_newsletters)

    return active_newsletters


def get_cached_unique_clients_count(cls):
    if not settings.CACHE_ENABLED:
        return cls.objects.all().distinct("email").count()

    key = 'unique_clients_count'
    unique_clients_count = cache.get(key)
    if unique_clients_count is None:
        unique_clients_count = cls.objects.all().distinct("email").count()
        cache.set(key, unique_clients_count)

    return unique_clients_count
