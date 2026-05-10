from django.contrib import admin

from .models import Movie, Session


def archive_movies(modeladmin, request, queryset):
    queryset.update(is_archived=True)


archive_movies.short_description = "Archive selected movies"


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ("title", "genre", "rating", "is_featured", "is_archived")
    list_filter = ("genre", "is_featured", "is_archived")
    search_fields = ("title", "genre", "description")
    actions = [archive_movies]


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ("movie", "theatre", "start_time", "end_time", "price", "seats_available", "is_active")
    list_filter = ("is_active", "theatre__cinema", "theatre")
    search_fields = ("movie__title", "theatre__name", "theatre__cinema__name")
