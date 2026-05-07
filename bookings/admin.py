from django.contrib import admin

from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("booking_ref", "user", "session", "quantity", "unit_price", "total_price", "status", "booked_at")
    list_filter = ("status", "booked_at")
    search_fields = ("booking_ref", "user__username", "session__movie__title")
