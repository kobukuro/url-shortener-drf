from django.db import models
from django.utils import timezone
from datetime import timedelta


class ShortURL(models.Model):
    original_url = models.URLField(max_length=2048)
    short_code = models.CharField(max_length=10, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expiration_date = models.DateTimeField()

    class Meta:
        indexes = [
            models.Index(fields=['short_code']),
            models.Index(fields=['expiration_date'])
        ]

    def save(self, *args, **kwargs):
        if not self.expiration_date:
            self.expiration_date = timezone.now() + timedelta(days=30)
        super().save(*args, **kwargs)
