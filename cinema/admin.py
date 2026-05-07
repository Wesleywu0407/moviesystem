from django.contrib import admin

from .models import Cinema, Theatre


@admin.register(Cinema)
class CinemaAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "phone", "is_active", "created_at")
    list_filter = ("city", "is_active")
    search_fields = ("name", "city", "address")


@admin.register(Theatre)
class TheatreAdmin(admin.ModelAdmin):
    list_display = ("name", "cinema", "capacity", "screen_type")
    list_filter = ("screen_type", "cinema")
    search_fields = ("name", "cinema__name")
