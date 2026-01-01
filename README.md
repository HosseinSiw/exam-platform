
# Online Exam & Assessment Platform

A **production-ready online examination and assessment system** designed for scalable test execution, async grading, and customizable authentication flows.

---

## What This Project Does

This web application allows organizations and instructors to create, manage, and run online exams with asynchronous grading and a fully customized authentication system.

Key goals:
- Handle real-world exam workflows
- Support custom authentication logic
- Scale safely under concurrent submissions

---

## Core Features

- Custom Django **User model**
- Custom **authentication backend**
- Exam & question management
- Asynchronous exam grading with Celery
- Result persistence and analysis
- Production-ready deployment with Docker

---

## Core Domain Models

- User
- Exam
- Question
- Answer
- Submission
- ExamResult

Models are designed around domain logic, not simple CRUD.

---

## Exam Submission Flow

User submits answers → Django stores submission → Celery grades asynchronously → Results stored in PostgreSQL

This ensures fast responses and non-blocking requests.

---

## Architecture

- Django + Gunicorn (application layer)
- Nginx (reverse proxy & static files)
- PostgreSQL (primary database)
- Redis (Celery broker)
- Celery (background processing)

All services run in isolated Docker containers.

---

## Tech Stack

- Python / Django
- PostgreSQL
- Redis
- Celery
- Nginx
- Gunicorn
- Docker & Docker Compose

---

## Running Locally

```bash
docker compose up --build
```

```bash
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py collectstatic
```

---

## Production Characteristics

- No Django runserver
- Logs via STDOUT
- Async task processing
- Docker-native networking
- Environment-based configuration

---

## Project Philosophy

This project is intended to represent a **real, production-backed Django system**, not a tutorial or demo project.

---

## License

MIT