from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("index/", views.index, name="index"),
    path("films/", views.films, name="films"),
    path("movies/", views.movie_list, name="movie_list"),
    path("movies/create/", views.movie_create, name="movie_create"),
    path("movies/<int:pk>/edit/", views.movie_edit, name="movie_edit"),
    path("movies/<int:pk>/delete/", views.movie_delete, name="movie_delete"),
    path("sessions/", views.session_list, name="session_list"),
    path("sessions/create/", views.session_create, name="session_create"),
    path("sessions/<int:pk>/edit/", views.session_edit, name="session_edit"),
    path("sessions/<int:pk>/delete/", views.session_delete, name="session_delete"),
    path("movie-detail/<int:movie_id>/", views.movie_detail, name="movie_detail_by_id"),
    path("movie-detail/", views.movie_detail, name="movie_detail"),
    path("directors/", views.directors, name="directors"),
    path("genres/", views.genres, name="genres"),
    path("booking/", views.booking, name="booking"),
    path("booking/confirmation/<str:booking_ref>/", views.booking_confirmation, name="booking_confirmation"),
    path("login/", views.login_page, name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="home"), name="logout"),
    path("register/", views.register_page, name="register"),
    path("ai-recommendations/", views.ai_recommendations, name="ai_recommendations"),
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("admin-panel/", views.admin_dashboard, name="admin_panel"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
