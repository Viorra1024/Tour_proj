# Simple Setup Guide for TourGid

Hey! 👋 Follow these steps to get the project running on your computer.

## Step 1: Install Required Software 🔧
First, you need to install some programs:

1. Install Python:
   - Go to https://www.python.org/downloads/
   - Download Python 3.8 or newer
   - During installation, check "Add Python to PATH"

2. Install Git:
   - Go to https://git-scm.com/downloads
   - Download and install Git for your operating system

3. Install Redis:
   - **For Windows:**
     - Go to https://github.com/microsoftarchive/redis/releases
     - Download and install the latest version
   - **For Mac:**
     - Open Terminal
     - Run: `brew install redis`
   - **For Linux:**
     - Open Terminal
     - Run: `sudo apt-get install redis-server`

## Step 2: Get the Project 📥

1. Open Terminal (or Command Prompt on Windows)

2. Clone the project:
   ```bash
   git clone https://github.com/yourusername/tourgid.git
   cd tourgid
   ```

## Step 3: Set Up the Project 🛠️

1. Create a virtual environment:
   ```bash
   # On Windows:
   python -m venv venv
   venv\Scripts\activate

   # On Mac/Linux:
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Create your environment file:
   ```bash
   # On Windows:
   copy .env.example .env

   # On Mac/Linux:
   cp .env.example .env
   ```

4. Open the `.env` file in a text editor and update these values:
   ```
   SECRET_KEY=make-up-a-random-string
   DEBUG=True
   GOOGLE_MAPS_API_KEY=your-google-maps-api-key
   ```

5. Set up the database:
   ```bash
   python manage.py migrate
   ```

6. Create an admin account:
   ```bash
   python manage.py createsuperuser
   ```
   - Enter your email
   - Create a password
   - Remember these details!

7. Load sample data (optional):
   ```bash
   python manage.py load_sample_data
   python manage.py load_sample_images
   ```

## Step 4: Start the Project 🚀

1. Start Redis:
   - **Windows:** Redis should start automatically
   - **Mac:** Run `brew services start redis`
   - **Linux:** Run `sudo service redis-server start`

2. Open three separate terminal windows and make sure you're in the project folder in each one.
   In each terminal, activate the virtual environment:
   ```bash
   # On Windows:
   venv\Scripts\activate

   # On Mac/Linux:
   source venv/bin/activate
   ```

3. In the first terminal, run the web server:
   ```bash
   python manage.py runserver
   ```

4. In the second terminal, run Celery worker:
   ```bash
   # On Windows:
   celery -A tourgid worker -l info -P solo

   # On Mac/Linux:
   celery -A tourgid worker -l info
   ```

5. In the third terminal, run Celery beat:
   ```bash
   celery -A tourgid beat -l info
   ```

## Step 5: Use the Website 🌐

1. Open your web browser and go to:
   - Main website: http://localhost:8000
   - Admin panel: http://localhost:8000/admin

2. Log in to the admin panel with the superuser account you created

## Common Problems & Solutions 🔍

1. If you see "pip not found":
   - Try using `pip3` instead of `pip`
   - Or try: `python -m pip install -r requirements.txt`

2. If Redis won't start:
   - Windows: Check Services app and start Redis manually
   - Mac/Linux: Try `redis-server` in a new terminal

3. If you see database errors:
   - Make sure you ran `python manage.py migrate`
   - Check if your database file exists

4. If you see "ModuleNotFoundError":
   - Make sure you activated the virtual environment
   - Try installing requirements again

## Need Help? 🆘

1. Check the `project_explanation.txt` file for detailed info
2. Look at error messages in the terminal
3. Check the project's README.md file
4. Ask your friend (the project owner) for help! 