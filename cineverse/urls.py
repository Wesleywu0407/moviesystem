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
