import os
from celery import Celery

# Nastavte výchozí Django settings modul pro program 'celery'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nandeback.settings')

app = Celery('nandeback')

# Načtěte konfiguraci z Django settings, použije prefix 'CELERY_'
app.config_from_object('django.conf:settings', namespace='CELERY')

# Automaticky načte úlohy ze všech registrovaných Django app configs
app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')