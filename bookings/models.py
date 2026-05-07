import secrets

from django.conf import settings
from django.db import models


class Booking(models.Model):
    STATUS_PENDING = "pending"
    STATUS_CONFIRMED = "confirmed"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_CONFIRMED, "Confirmed"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookings")
    session = models.ForeignKey("movies.Session", on_delete=models.CASCADE, related_name="bookings")
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    booked_at = models.DateTimeField(auto_now_add=True)
    booking_ref = models.CharField(max_length=20, unique=True, blank=True)

    class Meta:
        ordering = ["-booked_at"]

    def __str__(self):
        return f"{self.booking_ref} - {self.user}"

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        if not self.booking_ref:
            self.booking_ref = f"CV-{secrets.token_hex(4).upper()}"
        super().save(*args, **kwargs)
