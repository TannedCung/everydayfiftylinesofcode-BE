# everydayfiftylinesofcode-BE

## Project Overview
The "everydayfiftylinesofcode-BE" project is designed to encourage developers to write at least fifty lines of code every day. This backend service supports the tracking and management of daily coding activities, providing a structured way to maintain coding discipline and improve skills over time.

## Features
- User authentication and authorization
- Daily coding activity tracking
- Progress reports and analytics
- Integration with popular code repositories
- Notifications and reminders

## Getting Started

### Prerequisites
- Python 3.8+
- Django 3.2+
- PostgreSQL

### Installation
1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/everydayfiftylinesofcode-BE.git
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

5. Create a superuser:
    ```bash
    python manage.py createsuperuser
    ```

6. Run the development server:
    ```bash
    python manage.py runserver
    ```

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