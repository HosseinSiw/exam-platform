
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

This project is intended to represent a **real, production-backed Exam and Assessment Django system**


# سامانه آنلاین آزمون و ارزیابی

یک **پلتفرم آزمون و ارزیابی آنلاین با معماری Production‑Ready** که با Django توسعه داده شده و بر مقیاس‌پذیری، احراز هویت سفارشی و پردازش ناهمگام نتایج تمرکز دارد.

این پروژه صرفاً یک اپلیکیشن تمرینی نیست، بلکه یک سیستم بک‌اند واقعی با تصمیم‌های معماری آگاهانه است.

---

## 🎯 هدف پروژه

این سامانه به سازمان‌ها یا مدرسین امکان می‌دهد:

- تعریف و مدیریت آزمون‌ها و بانک سؤالات
- ثبت‌نام و احراز هویت کاربران با **مدل کاربر سفارشی**
- اعمال منطق احراز هویت خارج از محدودیت‌های Django پیش‌فرض
- برگزاری آزمون و ثبت پاسخ‌ها
- تصحیح آزمون‌ها به‌صورت **ناهمگام (Async)**
- ذخیره و تحلیل نتایج آزمون‌ها

---

## 👥 موارد استفاده

- سامانه‌های آزمون آنلاین
- آزمون‌های داخلی شرکت‌ها
- مراکز آموزشی
- سناریوهای پرترافیک با نیاز به پردازش ناهمگام

---

## 🧠 منطق دامنه (Business Logic)

### ✅ مدل کاربر سفارشی
- عدم استفاده مستقیم از AbstractUser پیش‌فرض
- طراحی‌شده برای توسعه‌پذیری (نقش‌ها، سطوح دسترسی، پروفایل‌ها)
- جداسازی منطق دامنه از فرضیات Django

### ✅ احراز هویت سفارشی
- Authentication Backend اختصاصی
- پشتیبانی از منطق احراز هویت مبتنی بر دامنه
- آماده‌ی توسعه برای MFA یا سرویس‌های خارجی

---

## 🧱 مدل‌های داده (خلاصه)

- User
- Exam
- Question
- Answer
- Submission
- ExamResult
- TaskResult (Celery)

مدل‌ها با تمرکز بر چرخه حیات داده و یکپارچگی طراحی شده‌اند، نه صرفاً CRUD.

---

## 🔁 جریان ثبت و تصحیح آزمون

کاربر ➜ ارسال پاسخ‌ها ➜ ذخیره در دیتابیس ➜ ارسال تسک Celery ➜

تصحیح ناهمگام ➜ ذخیره نتیجه

این معماری باعث:
- پاسخ‌دهی سریع API
- جلوگیری از بلاک شدن درخواست‌ها
- امکان retry و fault tolerance

---

## 🔐 احراز هویت و دسترسی

- User Model سفارشی
- Authentication Backend اختصاصی
- آماده برای Role-based یا Policy-based Authorization

---

## 🧩 دلایل انتخاب معماری

### Celery
برای جداسازی عملیات سنگین (تصحیح) از چرخه request/response.

### Redis
Broker سریع و سبک برای پردازش صف‌ها.

### PostgreSQL
دیتابیس قابل اعتماد با تضمین سازگاری داده.

### Nginx + Gunicorn
- Gunicorn برای اجرای WSGI
- Nginx برای Reverse Proxy و Static files

---

## 🛠 تکنولوژی‌ها

- Django
- PostgreSQL
- Celery + Redis
- Gunicorn
- Nginx
- Docker & Docker Compose

---

## 🚀 اجرای پروژه

```bash
docker compose up --build
```

```bash
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py collectstatic
```

---

## ✅ ویژگی‌های Production

- عدم استفاده از runserver
- پردازش ناهمگام تسک‌ها
- Static و Media اشتراکی
- لاگ‌گیری استاندارد Docker
- پیکربندی مبتنی بر Environment

---

## 🧠 سطح پروژه

تمرکز اصلی روی:
- مقیاس‌پذیری
- قابلیت نگهداری
- تصمیم‌های معماری شفاف
