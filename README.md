# TaskFlow - Django To-Do App.

TaskFlow is a polished Django CRUD application built for a portfolio. It helps users create, search, filter, prioritize, update, complete, and delete tasks through a responsive web interface.

## Features

- Create, edit, complete, and delete tasks
- Search by title or description
- Filter by status and priority
- Due dates, priority badges, and completion stats
- Django admin integration
- Responsive custom UI
- Production-friendly static file setup with WhiteNoise
- Test coverage for the model and core views

## Tech Stack

- Python 3
- Django 5
- supabase for backend
- WhiteNoise for static files
- Gunicorn-ready deployment dependency

## Architecture

TaskFlow is currently a server-rendered Django application using Django's MTV pattern:

- Models define task data and persistence
- Forms handle validation for tasks, login, and signup
- Views render HTML templates and process user actions
- Templates and static CSS provide the responsive frontend
- Django auth handles signup, login, logout, and admin access

There is no REST API layer in the current version of this app. Because the app does not expose API endpoints, Swagger/OpenAPI documentation is not included yet. If an API is added later, Swagger docs can be introduced for those endpoints.

## Getting Started

1. Clone the repository.

```bash
git clone https://github.com/your-username/taskflow-django.git
cd taskflow-django
```

2. Create and activate a virtual environment.

```bash
python -m venv .venv
.venv\Scripts\activate
```

3. Install dependencies.

```bash
python -m pip install -r requirements.txt
```

4. Run migrations.

```bash
python manage.py migrate
```

5. Start the development server.

```bash
python manage.py runserver
```

Open `http://127.0.0.1:8000/` in your browser.

## Admin

Create an admin user:

```bash
python manage.py createsuperuser
```

Then visit `http://127.0.0.1:8000/admin/`.

## Tests

```bash
python manage.py test
```

## Deployment Notes

Copy `.env.example` to `.env` locally or configure environment variables on your hosting provider:

- `SECRET_KEY`
- `DEBUG=False`
- `ALLOWED_HOSTS=your-domain.com`

Before deploying, run:

```bash
python manage.py collectstatic
```

## Portfolio Talking Points

- Clean Django MTV structure with reusable views and forms
- Search and filter logic using Django ORM queries
- Server-rendered responsive UI without frontend framework overhead
- Deployment-minded settings, static files, and documentation
- Automated tests for important user flows
