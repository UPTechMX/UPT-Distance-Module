
from __future__ import absolute_import, unicode_literals
import os
import sqlalchemy
from celery import Celery
from decouple import config

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ST.settings')

from django.db import connection as db

broker ="sqla+postgres://" + config('DB_USER') + ":" + config('DB_PASSWORD') + "@" + config('DB_HOST') + ":" + config('DB_PORT') + "/" + config('DB_NAME')
app = Celery('ST')

app.config_from_object('django.conf:settings', namespace='CELERY') 
app.autodiscover_tasks()  
app.conf.update(BROKER_URL=broker, worker_max_tasks_per_child=1, )
@app.task(bind=True)
def debug_task(self):
    print('Request: {0}'.format(self.request))

