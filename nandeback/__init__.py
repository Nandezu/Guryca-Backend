# Toto zajistí, že aplikace Celery je vždy importována při spuštění Django
from .celery import app as celery_app

__all__ = ('celery_app',)