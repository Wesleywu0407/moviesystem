# CINEVERSE Deployment Notes

## 1. Clone the repository

```bash
git clone https://github.com/Wesleywu0407/moviesystem.git
cd moviesystem
```

## 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 4. Create your `.env` file

Use `.env.example` as a guide, but do not commit `.env`.

```bash
cp .env.example .env
```

Then edit `.env` with real values:

```text
DJANGO_SECRET_KEY=your-real-secret-key
DJANGO_DEBUG=False
OPENAI_API_KEY=your-real-openai-key
ANTHROPIC_API_KEY=your-real-anthropic-key-if-used
DATABASE_URL=
```

For the current SQLite setup, `DATABASE_URL` can stay blank. If your deployment platform provides a database URL, paste it there.

## 5. Apply database migrations

```bash
python manage.py migrate
```

## 6. Collect static files

```bash
python manage.py collectstatic
```

## 7. Start with gunicorn

```bash
gunicorn cineverse.wsgi:application --bind 0.0.0.0:8000
```

The configured production host is:

```text
infs3202-0c24504d.uqcloud.net
```
