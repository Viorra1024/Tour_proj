# TourGid - Directory of Tourist

A comprehensive web application providing information about tourist destinations, hotels, attractions, and more. Built with Django, REST framework, Celery, and more.

## Prerequisites

- Python 3.8 or higher
- Redis (for Celery)
- Git

## Installation Steps

1. Clone the repository
   ```bash
   git clone https://github.com/yourusername/tourgid.git
   cd tourgid
   ```

2. Create and activate a virtual environment
   ```bash
   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate

   # On Windows
   python -m venv venv
   venv\Scripts\activate
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Open .env and update the variables with your values
   # Make sure to update:
   # - SECRET_KEY
   # - EMAIL settings
   # - GOOGLE_MAPS_API_KEY
   ```

5. Install and start Redis (required for Celery)
   ```bash
   # On macOS using Homebrew
   brew install redis
   brew services start redis

   # On Ubuntu/Debian
   sudo apt-get install redis-server
   sudo service redis-server start

   # On Windows
   # Download and install from https://redis.io/download
   ```

6. Set up the database
   ```bash
   python manage.py migrate
   ```

7. Create a superuser
   ```bash
   python manage.py createsuperuser
   ```

8. Load sample data (optional)
   ```bash
   python manage.py load_sample_data
   python manage.py load_sample_images
   ```

## Running the Application

1. Start the Django development server
   ```bash
   python manage.py runserver
   ```

2. Start Celery worker (in a new terminal)
   ```bash
   # Make sure your virtual environment is activated
   celery -A tourgid worker -l info
   ```

3. Start Celery sbeat for scheduled tasks (in a new terminal)
   ```bash
   # Make sure your virtual environment is activated
   celery -A tourgid beat -l info
   ```

4. Access the application:
   - Main site: http://localhost:8000
   - Admin interface: http://localhost:8000/admin
   - API documentation: http://localhost:8000/api/v1/swagger/

## Features

- **Destination Directory**: Browse and search tourist destinations worldwide
- **Hotel Database**: Find accommodations with detailed information and ratings
- **Interactive Map**: Explore attractions and hotels with Google Maps integration
- **Booking Integration**: Connect with external booking services
- **User Reviews**: Read and write reviews for destinations, hotels, and attractions
- **City Guides**: Automatically generated guides for popular destinations
- **Favorites**: Save your favorite places for future reference
- **REST API**: Full API access for all resources

## API Documentation

Once the server is running, you can access the API documentation at:
- Swagger UI: `http://localhost:8000/api/v1/swagger/`
- ReDoc: `http://localhost:8000/api/v1/redoc/`

## Running Tests

```bash
# Run all tests
python manage.py test

# Run specific test modules
python manage.py test tours.tests.test_api
python manage.py test tours.tests.test_security

# Run with coverage report
coverage run --source='.' manage.py test
coverage report
```

## Common Issues and Solutions

1. **Redis Connection Error**
   - Make sure Redis is installed and running
   - Check if the Redis service is running on port 6379

2. **Database Migrations**
   - If you get migration errors, try:
     ```bash
     python manage.py makemigrations
     python manage.py migrate
     ```

3. **Static/Media Files Not Loading**
   - Run `python manage.py collectstatic`
   - Make sure your web server is configured to serve static/media files

4. **Celery Worker Not Starting**
   - Check if Redis is running
   - Make sure you're in the virtual environment
   - On Windows, you might need to run: `celery -A tourgid worker -l info -P solo`

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

[MIT License](LICENSE) 