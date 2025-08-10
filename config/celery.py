# project_name/celery.py
import os
from celery import Celery

# Set the default Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")

# Load settings from Django settings with CELERY_ prefix
app.config_from_object("django.conf:settings", namespace="CELERY")

# Discover tasks from all installed apps
app.autodiscover_tasks()
