from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
import re
from datetime import timedelta

# ------------------------------
# ✅ 1. Lead Model
# ------------------------------
class Lead(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    interest = models.CharField(max_length=100)
    score = models.IntegerField(default=0)
    segment = models.CharField(max_length=50, blank=True, null=True)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.name} ({self.segment})"

    def compute_score_and_segment(self):
        score = 0
        interest_lower = self.interest.lower()

        if "buy" in interest_lower:
            score += 50
        if "demo" in interest_lower:
            score += 30
        if "info" in interest_lower:
            score += 10

        self.score = score

        if score >= 50:
            self.segment = 'Hot'
        elif 30 <= score < 50:
            self.segment = 'Warm'
        else:
            self.segment = 'Cold'

    def clean(self):
        phone_pattern = re.compile(r'^\+\d{10,15}$')
        if not phone_pattern.match(self.phone):
            raise ValidationError("Phone number must be in the format +1234567890 (10–15 digits).")

    def save(self, *args, **kwargs):
        self.compute_score_and_segment()
        super().save(*args, **kwargs)


# ------------------------------
# ✅ 2. WhatsApp Session Tracking
# ------------------------------
class WhatsAppSession(models.Model):
    phone = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    last_message_at = models.DateTimeField(auto_now=True)

    def is_session_active(self):
        return timezone.now() - self.last_message_at < timedelta(hours=24)

    def __str__(self):
        return f"{self.phone} - Active: {self.is_session_active()}"


# ------------------------------
# ✅ 3. Message Log
# ------------------------------
class MessageLog(models.Model):
    MESSAGE_TYPES = [
        ('initial', 'Initial'),
        ('followup1', '15-min Follow-up'),
        ('followup2', '1-hour Follow-up'),
        ('status_updated', 'Status Updated') 
    ]

    phone = models.CharField(max_length=20)
    name = models.CharField(max_length=100, blank=True)
    template_type = models.CharField(max_length=20, choices=MESSAGE_TYPES)
    status = models.CharField(max_length=10)  # sent or failed
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.phone} - {self.template_type} - {self.status}"
