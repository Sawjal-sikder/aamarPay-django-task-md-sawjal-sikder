# AamarPay Django Task

## Local Setup Instructions

### 1. Clone the Repository

```bash
# Clone your repo
$ git clone <your-repo-url>
$ cd aamarPay-django-task-md-sawjal-sikder
```

### 2. Create and Activate Virtual Environment

```bash
$ python3 -m venv venv
$ source venv/bin/activate
```

### 3. Install Dependencies

```bash
$ pip install -r requirements.txt
```

### 4. Apply Migrations

```bash
$ python manage.py makemigrations
$ python manage.py migrate
```

### 5. Create Superuser (Optional)

```bash
$ python manage.py createsuperuser
```

### 6. Run Development Server

```bash
$ python manage.py runserver
```

### 7. Run Production Server with Gunicorn

```bash
$ pip install gunicorn
$ gunicorn --bind 0.0.0.0:8000 config.wsgi:application --workers 4 --timeout 1200
```

- For best results, use a process manager like `supervisor` or `systemd` to keep Gunicorn running.
- Adjust `--workers` and `--timeout` as needed for your environment.

---

## Celery & Redis Setup

### 1. Install Redis

- On Ubuntu:
  ```bash
  $ sudo apt-get update
  $ sudo apt-get install redis-server
  $ sudo systemctl enable redis-server
  $ sudo systemctl start redis-server
  ```
- On MacOS:
  ```bash
  $ brew install redis
  $ brew services start redis
  ```

### 2. Install Celery

```bash
$ pip install celery
```

### 3. Add Celery Settings to `config/settings.py`

```python
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Dhaka'
```

### 4. Start Celery Worker

```bash
$ celery -A config worker --loglevel=info
```

---

## .env Example for Payment Info

Create a `.env` file in your project root with the following content:

```env
# AamarPay Payment Gateway Credentials
STORE_ID=aamarpaytest
SIGNATURE_KEY=dbb74894e82415a2f7ff0ec3a97e4183
ENDPOINT=https://sandbox.aamarpay.com/jsonpost.php
```

- Make sure to load these variables in your Django settings using `python-dotenv` or similar.
- Never commit your real production credentials to version control.

---

## How to Test the Payment Flow Using AamarPay Sandbox

1. **Start your Django server** (Gunicorn & Start Celery Worker)
2. **Access the payment initiation endpoint:**

   - Use Postman, curl, or your frontend to POST to:

     ```
     POST /api/initiate-payment/
     Content-Type: application/json
     Authorization: Bearer <your-jwt-token>

     ```

   - The response will include a `payment_url` for the AamarPay sandbox.

3. **Open the payment URL in your browser**
   - Complete the payment using sandbox credentials (test card, etc.)
4. **AamarPay will redirect to your callback endpoints:**
   - `/api/payment/success/` for successful payments
   - `/api/payment/fail/` for failed payments
   - `/api/payment/cancel/` for cancelled payments
5. **Verify the transaction in your Django dashboard**
   - `/api/dashboard/transition/` for payments transaction

---

## Postman Collection

You can use the following Postman collection to test all API endpoints easily:

[Payment API Postman Collection](https://documenter.getpostman.com/view/45067236/2sB3BEmUus)

https://documenter.getpostman.com/view/45067236/2sB3BEmUus

- Import this collection into Postman to access pre-configured requests for authentication, payment initiation, callbacks, and transaction verification.
- Update environment variables in Postman as needed for your local setup.

---
