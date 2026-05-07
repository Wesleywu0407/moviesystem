from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.db import transaction
from django.db.models import F
from django.shortcuts import redirect, render

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


def movie_detail(request):
    return render(request, "pages/movie-detail.html")


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


def ai_recommendations(request):
    return render(request, "pages/ai-recommendations.html")


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
@user_passes_test(lambda user: user.is_staff, login_url="home")
def admin_dashboard(request):
    return render(request, "pages/admin.html")
