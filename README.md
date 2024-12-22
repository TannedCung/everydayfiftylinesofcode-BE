# everydayfiftylinesofcode-BE

## Project Overview
The "everydayfiftylinesofcode-BE" project is designed to encourage developers to write at least fifty lines of code every day. This backend service supports the tracking and management of daily coding activities, providing a structured way to maintain coding discipline and improve skills over time.

## Features
- User authentication and authorization
- Daily coding activity tracking
- Progress reports and analytics
- Integration with popular code repositories
- Notifications and reminders
- Asynchronous task processing with Celery
- Automated GitHub activity tracking

## Prerequisites
- Python 3.8+
- Django 3.2+
- PostgreSQL
- Redis (for Celery)
- Docker & Docker Compose (optional)

### Project Structure
```
daily50/          # Main project directory
├── core/         # Core application
│   ├── tasks/    # Celery tasks
│   └── ...
├── daily50/      # Project configuration
│   ├── celery.py # Celery configuration
│   └── ...
└── docker/       # Docker configurations
```

### Installation
1. Clone the repository:
    ```bash
    git clone https://github.com/TannedCung/everydayfiftylinesofcode-BE.git
    cd everydayfiftylinesofcode-BE
    ```

2. Create and activate a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Set up the database:
    ```bash
    python manage.py migrate
    ```

# Start Django
python manage.py runserver

# Start Celery worker
celery -A daily50 worker -l INFO

# Start Celery beat (for periodic tasks)
celery -A daily50 beat -l INFO

### Usage
- Access the application at `http://127.0.0.1:8000/`
- Log in with your superuser credentials
- Start tracking your daily coding activities

## Contributing
We welcome contributions! Please read our [Contributing Guidelines](CONTRIBUTING.md) for more details.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact
For any inquiries or support, please contact us at support@everydayfiftylinesofcode.com.