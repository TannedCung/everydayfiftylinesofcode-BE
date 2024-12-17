FROM python:3.9

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY ../../requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY ../../ .

# Command to run the Celery worker
CMD ["celery", "-A", "daily50", "worker", "--loglevel=info"]├── core
│   ├── admin.py
│   ├── apps.py
│   ├── filters
│   ├── __init__.py
│   ├── migrations
│   ├── models
│   ├── __pycache__
│   ├── serializers
│   ├── tests.py
│   ├── urls.py
│   ├── utils
│   └── views
├── daily50
│   ├── asgi.py
│   ├── __init__.py
│   ├── __pycache__
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── db.sqlite3
├── load_env.sh
├── manage.py
├── README.md
└── requirements.txt