# Expense Tracker Command Reference

This document provides a list of commonly used commands for managing the Expense Tracker application. Follow the instructions below to perform various tasks.

---

## Celery Commands

    Start the Celery worker:
    ```bash
    celery -A expense_tracker worker --loglevel=info -Q tasks 
    ```

    Start the Celery beat scheduler:
    ```bash
    celery -A expense_tracker beat --loglevel=info
    ```

---

## Django Development Server

Run the development server:
```bash
python manage.py runserver
```

Start Tailwind for CSS development:
```bash
python manage.py tailwind start
```

---

## Redis Server Management

Enable Redis to start on boot:
```bash
sudo systemctl enable redis-server
```

Start the Redis server:
```bash
sudo systemctl start redis-server
```

Check the status of the Redis server:
```bash
sudo systemctl status redis-server
```

Stop the Redis server:
```bash
sudo systemctl stop redis-server
```

Disable Redis from starting on boot:
```bash
sudo systemctl disable redis-server
```

Restart the Redis server:
```bash
sudo systemctl restart redis-server
```

---

## Database Management

Make migrations for database changes:
```bash
python manage.py makemigrations
```

Apply migrations to the database:
```bash
python manage.py migrate
```

---

## Django Shell

Access the Django shell:
```bash
python manage.py shell
```

Run the following commands in the shell to send email alerts:
```python
from users.tasks import send_alerts_via_email
send_alerts_via_email()
```

---

**Note:** Ensure that all required services (e.g., Redis) are running before executing commands that depend on them.