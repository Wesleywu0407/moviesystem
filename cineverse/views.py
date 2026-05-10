import json
import re

from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render
from openai import OpenAI

from accounts.forms import CineverseUserCreationForm
from bookings.models import Booking
from movies.models import Movie, Session


class MovieForm(forms.ModelForm):
    class Meta:
        model = Movie
        fields = [
            "title",
            "description",
            "duration_mins",
            "genre",
            "rating",
            "poster_url",
            "release_date",
            "is_featured",
        ]
        widgets = {
            "release_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "description": forms.Textarea(attrs={"rows": 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["release_date"].input_formats = ["%Y-%m-%d"]
        placeholders = {
            "title": "Film title",
            "description": "Synopsis for the film collection",
            "duration_mins": "120",
            "genre": "Drama",
            "rating": "PG-13",
            "poster_url": "https://...",
        }
        for name, field in self.fields.items():
            field.widget.attrs.setdefault("class", "admin-form-control")
            if name in placeholders:
                field.widget.attrs.setdefault("placeholder", placeholders[name])


class SessionForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = [
            "movie",
            "theatre",
            "start_time",
            "end_time",
            "price",
            "seats_available",
            "is_active",
        ]
        widgets = {
            "start_time": forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
            "end_time": forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["start_time"].input_formats = ["%Y-%m-%dT%H:%M"]
        self.fields["end_time"].input_formats = ["%Y-%m-%dT%H:%M"]
        placeholders = {
            "price": "18.00",
            "seats_available": "120",
        }
        for name, field in self.fields.items():
            field.widget.attrs.setdefault("class", "admin-form-control")
            if name in placeholders:
                field.widget.attrs.setdefault("placeholder", placeholders[name])


staff_required = user_passes_test(lambda u: u.role in ["staff", "admin"], login_url="home")


def home(request):
    return render(request, "pages/home.html")


def index(request):
    return render(request, "pages/index.html")


def films(request):
    movies = Movie.objects.filter(is_archived=False).order_by("-release_date")
    return render(request, "pages/films.html", {"movies": movies})


@login_required(login_url="login")
@staff_required
def movie_list(request):
    movies = Movie.objects.filter(is_archived=False).order_by("-release_date", "title")
    return render(request, "pages/movie_list.html", {"movies": movies})


@login_required(login_url="login")
@staff_required
def movie_create(request):
    form = MovieForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        movie = form.save()
        messages.success(request, f"{movie.title} has been added to CINEVERSE.")
        return redirect("movie_list")

    return render(
        request,
        "pages/movie_form.html",
        {"form": form, "form_title": "Add New Movie", "submit_label": "Create Movie"},
    )


@login_required(login_url="login")
@staff_required
def movie_edit(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    form = MovieForm(request.POST or None, instance=movie)
    if request.method == "POST" and form.is_valid():
        movie = form.save()
        messages.success(request, f"{movie.title} has been updated.")
        return redirect("movie_list")

    return render(
        request,
        "pages/movie_form.html",
        {"form": form, "movie": movie, "form_title": "Edit Movie", "submit_label": "Save Changes"},
    )


@login_required(login_url="login")
@staff_required
def movie_delete(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    if request.method == "POST":
        movie.is_archived = True
        movie.save()
        messages.success(request, f"{movie.title} has been archived.")
        return redirect("movie_list")

    return render(request, "pages/movie_confirm_delete.html", {"movie": movie})


@login_required(login_url="login")
@staff_required
def session_list(request):
    sessions = (
        Session.objects.filter(is_archived=False)
        .select_related("movie", "theatre", "theatre__cinema")
        .order_by("start_time")
    )
    return render(request, "pages/session_list.html", {"sessions": sessions})


@login_required(login_url="login")
@staff_required
def session_create(request):
    form = SessionForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        session = form.save()
        messages.success(request, f"Session for {session.movie.title} has been created.")
        return redirect("session_list")

    return render(
        request,
        "pages/session_form.html",
        {"form": form, "form_title": "Add New Session", "submit_label": "Create Session"},
    )


@login_required(login_url="login")
@staff_required
def session_edit(request, pk):
    session = get_object_or_404(Session.objects.select_related("movie"), pk=pk)
    form = SessionForm(request.POST or None, instance=session)
    if request.method == "POST" and form.is_valid():
        session = form.save()
        messages.success(request, f"Session for {session.movie.title} has been updated.")
        return redirect("session_list")

    return render(
        request,
        "pages/session_form.html",
        {"form": form, "session_obj": session, "form_title": "Edit Session", "submit_label": "Save Changes"},
    )


@login_required(login_url="login")
@staff_required
def session_delete(request, pk):
    session = get_object_or_404(Session.objects.select_related("movie", "theatre"), pk=pk)
    if request.method == "POST":
        session.is_archived = True
        session.save()
        messages.success(request, f"Session for {session.movie.title} has been archived.")
        return redirect("session_list")

    return render(request, "pages/session_confirm_delete.html", {"session_obj": session})


def movie_detail(request, movie_id=None):
    movie = None

    if movie_id is not None:
        movie = get_object_or_404(Movie, id=movie_id)
    else:
        title = request.GET.get("title", "").strip()
        if title:
            movie = Movie.objects.filter(title__iexact=title, is_archived=False).first()

    if movie is None:
        movie = Movie.objects.filter(is_archived=False).order_by("-release_date").first()

    return render(request, "pages/movie-detail.html", {"movie": movie})


def directors(request):
    return render(request, "pages/directors.html")


def genres(request):
    return render(request, "pages/genres.html")


def login_page(request):
    form = AuthenticationForm(request, data=request.POST or None)
    form.fields["username"].widget.attrs.update(
        {
            "id": "login-email",
            "class": "auth-input",
            "placeholder": "you@example.com",
            "required": True,
        }
    )
    form.fields["password"].widget.attrs.update(
        {
            "id": "login-password",
            "class": "auth-input",
            "placeholder": "Enter your password",
            "required": True,
        }
    )
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        messages.success(request, "Welcome back to Cineverse.")
        return redirect("home")

    return render(request, "pages/login.html", {"form": form})


def register_page(request):
    form = CineverseUserCreationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Your account has been created.")
        return redirect("home")

    return render(request, "pages/register.html", {"form": form})


def _parse_ai_json_recommendations(raw_text):
    if not raw_text:
        return []

    cleaned = raw_text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("[")
        end = cleaned.rfind("]")
        if start != -1 and end != -1 and end > start:
            try:
                parsed = json.loads(cleaned[start : end + 1])
            except json.JSONDecodeError:
                return []
        else:
            return []

    if isinstance(parsed, list):
        return parsed
    if isinstance(parsed, dict):
        return parsed.get("recommendations", [])
    return []


def ai_recommendations(request):
    movies = Movie.objects.filter(is_archived=False)
    recommended = []
    user_history = []

    if request.user.is_authenticated:
        bookings = Booking.objects.filter(user=request.user).select_related("session__movie")
        user_history = [booking.session.movie.title for booking in bookings]

    movie_list = [f"{movie.title} ({movie.genre}, rating {movie.rating})" for movie in movies]

    if user_history:
        prompt = f"""User watched: {', '.join(set(user_history))}.
Available movies: {', '.join(movie_list)}.
Recommend 3 movies with reasons.
Reply ONLY in JSON format, no markdown:
[{{"title": "Movie Title", "reason": "Why they will love it", "match": 95}}]"""
    else:
        prompt = f"""Available movies: {', '.join(movie_list)}.
Recommend 3 movies for a new cinema user.
Reply ONLY in JSON format, no markdown:
[{{"title": "Movie Title", "reason": "Why they will love it", "match": 90}}]"""

    try:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
        )
        raw = response.choices[0].message.content
        recommended = _parse_ai_json_recommendations(raw)[:3]
    except Exception as e:
        import logging

        logger = logging.getLogger(__name__)
        logger.error(f"AI recommendation error: {e}")
        print(f"AI ERROR: {e}")  # also print to console
        recommended = []

    return render(
        request,
        "pages/ai-recommendations.html",
        {
            "recommended": recommended,
            "user_history": user_history,
            "movies": movies,
            "ai_used": bool(recommended),
        },
    )


@login_required(login_url="login")
def booking(request):
    sessions = (
        Session.objects.filter(is_active=True, is_archived=False, seats_available__gt=0, movie__is_archived=False)
        .select_related("movie", "theatre", "theatre__cinema")
        .annotate(unit_price=F("price"))
        .order_by("start_time")
    )

    if request.method == "POST":
        session_id = request.POST.get("session_id")
        quantity_raw = request.POST.get("quantity", "1")

        if not session_id:
            messages.error(request, "Please select a session before confirming your booking.")
            return render(request, "pages/booking.html", {"sessions": sessions, "selected_session_id": ""})

        try:
            quantity = int(quantity_raw)
            if quantity < 1:
                raise ValueError
        except ValueError:
            messages.error(request, "Please enter a valid ticket quantity.")
            return render(request, "pages/booking.html", {"sessions": sessions, "selected_session_id": session_id})

        try:
            with transaction.atomic():
                chosen_session = (
                    Session.objects.select_for_update()
                    .select_related("movie", "theatre", "theatre__cinema")
                    .get(id=session_id, is_active=True, is_archived=False, movie__is_archived=False)
                )

                if chosen_session.seats_available < quantity:
                    messages.error(
                        request,
                        f"Only {chosen_session.seats_available} seat(s) left for this session.",
                    )
                    return render(
                        request,
                        "pages/booking.html",
                        {"sessions": sessions, "selected_session_id": session_id},
                    )

                booking_record = Booking.objects.create(
                    user=request.user,
                    session=chosen_session,
                    quantity=quantity,
                    unit_price=chosen_session.price,
                    total_price=chosen_session.price * quantity,
                    status=Booking.STATUS_CONFIRMED,
                )

                chosen_session.seats_available -= quantity
                chosen_session.save(update_fields=["seats_available"])
        except Session.DoesNotExist:
            messages.error(request, "Selected session is no longer available.")
            return render(request, "pages/booking.html", {"sessions": sessions, "selected_session_id": session_id})

        return redirect("booking_confirmation", booking_ref=booking_record.booking_ref)

    return render(request, "pages/booking.html", {"sessions": sessions})


@login_required(login_url="login")
def booking_confirmation(request, booking_ref):
    booking_record = (
        Booking.objects.select_related("session", "session__movie", "session__theatre", "session__theatre__cinema")
        .filter(booking_ref=booking_ref, user=request.user)
        .first()
    )
    if not booking_record:
        messages.error(request, "Booking confirmation not found.")
        return redirect("booking")

    return render(request, "pages/booking-confirmation.html", {"booking": booking_record})


@login_required(login_url="login")
@staff_required
def admin_dashboard(request):
    movies = Movie.objects.filter(is_archived=False).order_by("-release_date", "title")
    sessions = Session.objects.filter(is_archived=False).select_related("movie", "theatre").order_by("start_time")
    return render(request, "pages/admin.html", {"movies": movies, "sessions": sessions})
