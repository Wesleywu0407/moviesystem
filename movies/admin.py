from django.contrib import admin

from .models import Movie, Session


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ("title", "genre", "rating", "release_date", "is_featured")
    list_filter = ("genre", "is_featured", "release_date")
    search_fields = ("title", "genre", "description")


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ("movie", "theatre", "start_time", "end_time", "price", "seats_available", "is_active")
    list_filter = ("is_active", "theatre__cinema", "theatre")
    search_fields = ("movie__title", "theatre__name", "theatre__cinema__name")
