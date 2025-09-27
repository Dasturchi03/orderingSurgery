import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()


import random
from backend.models import *
from string import ascii_lowercase
from datetime import date, timedelta
from backend.functions import get_next_surgery_day


def get_word_random():
    return ''.join([random.choice(ascii_lowercase) for _ in range(random.randint(8, 12))])



for s in Surgeon.objects.all():
    br = Branch.objects.filter(id=s.branche.id)
    s.branch.set(br)
    s.save()


