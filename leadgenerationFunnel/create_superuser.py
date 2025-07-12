# leadgenerationFunnel/create_superuser.py

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'leadgenerationFunnel.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

username = "admin"
email = "admin@example.com"
password = "admin1234"

if not User.objects.filter(username=username).exists():
    print("Creating superuser...")
    User.objects.create_superuser(username=username, email=email, password=password)
else:
    print("Superuser already exists.")
