# CINEVERSE Django Project

Django project scaffold for a cinema booking platform with a black/gold CINEVERSE template system.

## Apps and Models

- `accounts`
  - Custom `User` model extending `AbstractUser`
  - `role` field with choices: `customer`, `staff`, `admin`
- `cinema`
  - `Cinema`: `name`, `address`, `city`, `phone`, `is_active`, `created_at`
  - `Theatre`: `cinema`, `name`, `capacity`, `screen_type`
- `movies`
  - `Movie`: `title`, `description`, `duration_mins`, `genre`, `rating`, `poster_url`, `release_date`, `is_featured`
  - `Session`: `movie`, `theatre`, `start_time`, `end_time`, `price`, `seats_available`, `is_active`
- `bookings`
  - `Booking`: `user`, `session`, `quantity`, `unit_price`, `total_price`, `status`, `booked_at`, `booking_ref`

All models are registered in Django admin.

## Database (MySQL)

Configured in `cineverse/settings.py`:

- Database name: `cineverse_db`
- User: `root`
- Host: `127.0.0.1`
- Port: `3306`

## Static, Templates, and Media

- Shared base template: `templates/base.html`
- Converted page templates: `templates/pages/*.html`
- Static files:
  - CSS: `static/css/style.css`
  - JS: `static/js/script.js`
  - Assets: `static/assets/*`
- Media upload config:
  - `MEDIA_URL = "media/"`
  - `MEDIA_ROOT = BASE_DIR / "media"`

## Setup

1. Install dependencies:

```bash
python3 -m pip install django pymysql
```

2. Create MySQL database:

```sql
CREATE DATABASE cineverse_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

3. Run migrations:

```bash
python3 manage.py migrate
```

4. Create superuser:

```bash
python3 manage.py createsuperuser
```

5. Start development server:

```bash
python3 manage.py runserver
```

6. Access admin:

- Django admin: `http://127.0.0.1:8000/django-admin/`

## Notes

- This project uses `PyMySQL` (`pymysql.install_as_MySQLdb()`) so it can connect to MySQL without compiling `mysqlclient`.
- Existing CINEVERSE HTML files were converted into Django templates that extend `base.html` and use `{% block %}`, `{% url %}`, and `{% static %}` tags.
