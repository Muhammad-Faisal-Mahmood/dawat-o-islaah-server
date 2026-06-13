import os
from celery import Celery

# Set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dawat_o_islaah.settings')

app = Celery('dawat_o_islaah')

# Use a string here so the worker doesn't have to serialize
# the object when using Windows.
app.config_from_object('django.conf:settings', namespace='CELERY')

# This is the magic line that finds your tasks.py files
app.autodiscover_tasks()