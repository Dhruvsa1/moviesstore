# GT Movies Store

CS 2340 tutorial project by Dhruvsai Dhulipudi, based on **Django 5 for the Impatient, Second Edition** by Daniel Correa and Greg Lim (Packt, 2024), through Chapter 13.

- Portfolio: https://www.dhruvsa1.org/
- Project description, process, and demo: https://www.dhruvsa1.org/moviesstore
- Live application: https://ddhruvsa1.pythonanywhere.com/
- Source: https://github.com/Dhruvsa1/moviesstore

## Run locally

Use Python 3.10–3.12. Verification used Python 3.12 and Django 5.0; PythonAnywhere uses Python 3.10 and Django 5.0. Python 3.14 is not a supported runtime for this pinned tutorial version.

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe manage.py migrate
.venv\Scripts\python.exe manage.py seed_movies
.venv\Scripts\python.exe manage.py runserver
```

On macOS/Linux, use `.venv/bin/python` in place of `.venv\Scripts\python.exe`. Open http://127.0.0.1:8000/.

The submission ZIP includes a migrated SQLite database containing only four movie records. It has no user accounts, sessions, orders, or reviews. A fresh Git clone can recreate the catalog with `seed_movies`, which does not replace existing records. Uploaded poster assets are included in `media/movie_images/`.

Register through **Sign Up**. To use `/admin/`, create your own administrator:

```powershell
.venv\Scripts\python.exe manage.py createsuperuser
```

No shared administrator credentials are included. Each checkout generates its own ignored `.secret-key`, unless `DJANGO_SECRET_KEY` is provided in the environment.

## Features

- Home and About pages with shared Bootstrap navigation and styling.
- Movie catalog, case-insensitive name search, movie details and posters.
- Signup, login, logout, and authenticated order history.
- Review creation, reading, editing, and deletion with owner checks.
- Session-based cart quantities, totals, and clearing.
- Simulated checkout, order confirmation, saved orders and item records.
- Django administration for movies, reviews, orders, items, users, and groups.

Purchases do not charge money. Streaming, rentals, and recommendations mentioned in the textbook's sample About copy are not implemented features.

## Verification

```powershell
.venv\Scripts\python.exe manage.py check
.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.venv\Scripts\python.exe manage.py test home
```

Seven integration tests cover public pages/search, account lifecycle, authentication redirects, review CRUD and ownership, cart totals/checkout/private orders, clearing/empty checkout, and admin access. See `docs/TUTORIAL_AUDIT.md` for the comparison and deliberate differences.

## PythonAnywhere deployment

The deployed app follows Chapter 13's GitHub → PythonAnywhere workflow.

1. Clone this repository into `/home/ddhruvsa1/moviesstore`.
2. Create/select `/home/ddhruvsa1/.virtualenvs/moviesstoreenv` using Python 3.10 and install `requirements.txt` there.
3. Run `python manage.py migrate`, `python manage.py seed_movies`, and `python manage.py collectstatic --noinput` in the virtual environment.
4. Use `deploy/pythonanywhere_wsgi.py` as `/var/www/ddhruvsa1_pythonanywhere_com_wsgi.py`. It selects `moviesstore.settings` and sets `DJANGO_DEBUG=false`.
5. Select the virtualenv on the Web tab. The WSGI configuration adds the project directory to Python's import path.
6. Map `/static/` to `/home/ddhruvsa1/moviesstore/static/` and `/media/` to `/home/ddhruvsa1/moviesstore/media/`.
7. Reload the web app and check the public URL.

When updating, back up the database, pull the code, apply migrations, collect static files, then reload. Do not replace a live database with the clean submission database.

PythonAnywhere's free site must be renewed from the Web tab monthly. Its displayed expiry at delivery was **October 13, 2026**.

## Tutorial scope and attribution

The core feature implementation and templates intentionally preserve the book's completed project. Django 5.0 is pinned for textbook fidelity; this educational implementation should be upgraded and further hardened before being used for a real commercial store. In particular, the book uses GET links for several state-changing operations and minimal server-side cart validation.

Original example code: https://github.com/PacktPublishing/Django-5-for-the-Impatient-Second-Edition/tree/main/Chapter12/moviesstore

Book: https://learning.oreilly.com/library/view/django-5-for/9781835461556/B22457_01.xhtml

Packt's MIT license is retained in `LICENSE`. Final code auditing, deployment repair, automated verification, portfolio preparation, and demo production were completed with coding-assistant support.
