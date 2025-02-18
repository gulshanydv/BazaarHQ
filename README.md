
# Product Showcase Django Project

This is a Django-based project for showcasing products. Follow the instructions below to set up and run the project locally.

## Prerequisites

Make sure you have the following installed:
- Python 3.12 (or newer)
- pip (Python package manager)
- Django
- MySQL (or your preferred database)

## Setup Instructions

### 1. Clone the Repository
Clone the repository to your local machine:
git clone https://github.com/gulshanydv/BazaarHQ.git
cd BazaarHQ

2. Create a Virtual Environment
It's recommended to use a virtual environment to keep the project dependencies isolated:
python3 -m venv venv
Activate the virtual environment:

On Linux/macOS:
source venv/bin/activate

On Windows:
venv\Scripts\activate

3. Install Project Dependencies
Install all the required dependencies from requirements.txt:
pip install -r requirements.txt


4. Set Up the .env File
Create a .env file in the root directory of the project and add the following environment variables:

DJANGO_SECRET_KEY=your-secret-key
DEBUG=True

DB_NAME=your-db-name
DB_USER=your-db-username
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=3306

EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-email-password
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_PHONE_NUMBER=your-twilio-phone-number

SOCIAL_AUTH_GOOGLE_CLIENT_ID=your-google-client-id
SOCIAL_AUTH_GOOGLE_SECRET=your-google-secret
Replace the placeholders (your-secret-key, your-db-name, etc.) with your actual credentials and keys.
Make sure to keep your .env file private and don't commit it to the repository.

5. Migrate the Database
Run the following command to set up the database tables:
python manage.py migrate
This will apply any database migrations and set up the required tables for the project.

6. Create a Superuser
If you want to access the Django admin panel, you can create an admin user:
python manage.py createsuperuser
Follow the prompts to set the username, email, and password for the superuser.

7. Run the Development Server
Start the Django development server:
python manage.py runserver
Now, you should be able to access the project in your browser at http://localhost:8000.

User Roles
Superuser: The superuser will have full access to the Django Admin panel, including the ability to post products and manage everything.
Regular User: Regular users can have limited permissions, such as only viewing and possibly posting products, depending on how you configure user roles and permissions in the Django Admin panel.
