VTU Project

A mobile-built VTU (Virtual Top Up) web application developed with Django, Paystack, and the GSubz API.

This project allows users to:

- Fund wallets using Paystack
- Purchase mobile data plans
- View transaction history
- Authenticate securely
- Reset forgotten passwords
- Interact with dynamically loaded data plans

One unique aspect of this project is that it was primarily developed using an Android phone with Termux.

---

Features

Authentication

- User registration
- Login/logout system
- Password reset functionality
- Session authentication

Wallet System

- Wallet creation per user
- Wallet funding with Paystack
- Automatic balance updates via webhook
- Funding history

VTU Services

- Buy data bundles
- Dynamic data plan loading
- Multiple network support
- Transaction logging

Networks Supported

- MTN SME
- MTN Gifting
- Airtel SME
- Glo Data
- Glo SME
- 9mobile

Transaction Features

- Debit/Credit tracking
- Recent transaction history
- Transaction status monitoring

---

Tech Stack

Backend

- Python
- Django
- Django REST Framework

Frontend

- HTML
- CSS
- JavaScript

APIs & Services

- Paystack
- GSubz API

Database

- SQLite (development)

---

Project Structure

vtu_project/
- │
- ├── manage.py
- ├── vtu_project/
- │
- ├── services/
- │   ├── templates/
- │   ├── static/
- │   │   ├── css/
- │   │   └── js/
- │   ├── models.py
- │   ├── views.py
- │   ├── urls.py
- │   ├── forms.py
- │   ├── gsubz.py
- │   └── ...

---

Installation

Clone Repository

git clone https://github.com/Demian091/Poly_vtu.git
cd Poly_vtu

---

Create Virtual Environment

- python -m venv venv

Activate:

Linux / Termux

source venv/bin/activate

Windows

venv\Scripts\activate

---

Install Dependencies

pip install -r requirements.txt

---

Configure Environment Variables

Create a ".env" file or configure settings with:

- SECRET_KEY= 
- DEBUG=False
- ALLOWED_HOSTS=
- GSUBZ_API_KEY= 
- GSUBZ_BASE_URL= https://gsubz.com/api
- PAYSTACK_PUBLIC_KEY= 
- PAYSTACK_SECRET_KEY= 
- EMAIL_HOST_USER= 
- EMAIL_HOST_PASSWORD= 
- DATABASE_URL=sqlite:///db.sqlite3


---

Run Migrations

- python manage.py makemigrations
- python manage.py migrate

---

Create Superuser

python manage.py createsuperuser

---

Start Development Server

python manage.py runserver

---

Paystack Webhook

Webhook URL:

/payment/webhook/

Configure this webhook in your Paystack dashboard.

---

API Endpoints

Authentication

- "/login/"
- "/register/"
- "/logout/"

Wallet

- "/api/fund-wallet/"
- "/payment/webhook/"

Data Services

- "/api/get-plans/"
- "/api/buy_data/"

---

Screenshots

Add screenshots here later:

- Dashboard
- Wallet funding
- Data purchase flow
- Transaction history

---

Future Improvements

- Celery task queue integration
- Password recovery 
- Redis caching
- Better frontend UI
- Admin analytics dashboard
- Email notifications
- Receipt generation
- Dark mode
- Airtime purchase
- Electricity bill payments

---

Challenges Faced

Some major challenges encountered during development:

- Paystack webhook handling
- Decimal vs float issues
- Dynamic data plan loading
- Mobile-only development workflow
- API reliability and DNS issues
- Frontend asynchronous updates

---

Inspiration

This project was built as part of a learning journey into:

- Backend development
- Fintech systems
- API integration
- Real-world Django applications

It also demonstrates that meaningful software projects can be built even with limited hardware resources.

---

Author

Polycarp Ifeanyi Emmanuel Ogochukwu

Computer Science Student | Backend Developer | Django Enthusiast

---

License

This project is open source and available under the MIT License.
