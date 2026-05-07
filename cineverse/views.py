import json
import os
import re
from collections import Counter

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render

from accounts.forms import CineverseUserCreationForm
from bookings.models import Booking
from movies.models import Movie, Session


def home(request):
    return render(request, "pages/home.html")


def index(request):
    return render(request, "pages/index.html")


def films(request):
    movies = Movie.objects.all().order_by("-release_date")
    return render(request, "pages/films.html", {"movies": movies})


def movie_detail(request, movie_id=None):
    movie = None

    if movie_id is not None:
        movie = get_object_or_404(Movie, id=movie_id)
    else:
        title = request.GET.get("title", "").strip()
        if title:
            movie = Movie.objects.filter(title__iexact=title).first()

    if movie is None:
        movie = Movie.objects.order_by("-release_date").first()

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


def _extract_text_from_anthropic_message(message):
    content_blocks = getattr(message, "content", []) or []
    text_chunks = []
    for block in content_blocks:
        if getattr(block, "type", "") == "text":
            text_chunks.append(getattr(block, "text", ""))
    return "\n".join(text_chunks).strip()


def _parse_ai_json_recommendations(raw_text):
    if not raw_text:
        return {}

    cleaned = raw_text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(cleaned[start : end + 1])
            except json.JSONDecodeError:
                return {}
    return {}


@login_required(login_url="login")
def ai_recommendations(request):
    all_movies = list(Movie.objects.all().order_by("-release_date"))
    booking_qs = Booking.objects.filter(user=request.user).select_related("session__movie")

    booked_movies = []
    seen_ids = set()
    for booking in booking_qs:
        movie = booking.session.movie
        if movie.id not in seen_ids:
            booked_movies.append(movie)
            seen_ids.add(movie.id)

    booked_titles = [movie.title for movie in booked_movies]
    preferred_genres = [movie.genre for movie in booked_movies if movie.genre]
    top_genres = [genre for genre, _ in Counter(preferred_genres).most_common(3)]

    candidates = [movie for movie in all_movies if movie.id not in seen_ids]
    if not candidates:
        candidates = all_movies

    recommendations = []
    ai_used = False

    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if api_key and candidates:
        try:
            import anthropic

            client = anthropic.Anthropic(api_key=api_key)

            candidate_lines = []
            for movie in candidates:
                candidate_lines.append(
                    f"- id: {movie.id}, title: {movie.title}, genre: {movie.genre}, rating: {movie.rating}, duration_mins: {movie.duration_mins}, description: {movie.description[:180]}"
                )

            prompt = (
                "You are a movie recommendation assistant for CINEVERSE.\n"
                f"User booked movies: {booked_titles if booked_titles else 'None yet'}.\n"
                f"User preferred genres (inferred): {top_genres if top_genres else 'Unknown'}.\n\n"
                "Recommend exactly 3 movies from this existing database only:\n"
                + "\n".join(candidate_lines)
                + "\n\nReturn ONLY valid JSON in this format:\n"
                '{\n  "recommendations": [\n    {"id": 1, "match": 92, "reason": "short reason"},\n    {"id": 2, "match": 88, "reason": "short reason"},\n    {"id": 3, "match": 85, "reason": "short reason"}\n  ]\n}'
            )

            message = client.messages.create(
                model="claude-opus-4-5",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )

            raw_text = _extract_text_from_anthropic_message(message)
            parsed = _parse_ai_json_recommendations(raw_text)

            candidate_map = {movie.id: movie for movie in candidates}
            for item in parsed.get("recommendations", [])[:3]:
                movie_id = item.get("id")
                movie = candidate_map.get(movie_id)
                if not movie:
                    continue
                recommendations.append(
                    {
                        "movie": movie,
                        "match": item.get("match", 85),
                        "reason": item.get("reason", "Recommended based on your booking history."),
                    }
                )

            ai_used = len(recommendations) > 0
        except Exception:
            ai_used = False

    if not recommendations:
        # Fallback recommender if API key isn't set or API parsing fails.
        genre_set = set(top_genres)
        ranked = []
        for movie in candidates:
            score = 80
            if movie.genre in genre_set:
                score += 10
            if movie.is_featured:
                score += 5
            ranked.append((score, movie))

        ranked.sort(key=lambda item: item[0], reverse=True)
        for score, movie in ranked[:3]:
            reason = (
                f"Because you often watch {movie.genre} films."
                if movie.genre in genre_set
                else "Popular pick from the CINEVERSE catalog."
            )
            recommendations.append({"movie": movie, "match": score, "reason": reason})

    context = {
        "recommendations": recommendations,
        "booked_titles": booked_titles,
        "top_genres": top_genres,
        "ai_used": ai_used,
    }
    return render(request, "pages/ai-recommendations.html", context)


@login_required(login_url="login")
def booking(request):
    sessions = (
        Session.objects.filter(is_active=True, seats_available__gt=0)
        .select_related("movie", "theatre", "theatre__cinema")
        .annotate(unit_price=F("price"))
        .order_by("start_time")
    )

    if request.method == "POST":
        session_id = request.POST.get("session_id")
        quantity_raw = request.POST.get("quantity", "1")

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
                    .get(id=session_id, is_active=True)
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
@user_passes_test(lambda u: u.role in ["admin", "staff"], login_url="home")
def admin_dashboard(request):
    return render(request, "pages/admin.html")
