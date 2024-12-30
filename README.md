# Venture: Event Management System

**Venture** is a Flask-based web application designed to simplify event management for users and organizers. With secure user authentication, role-based permissions, and an intuitive interface, Venture offers tools for creating, managing, and attending events.

## Features

### User Management
- Secure user registration and login with hashed passwords.
- Role-based access:
  - **Users** can view and participate in events.
  - **Organizers** can create, update, and delete events.

### Event Management
- Organizers can perform full CRUD operations for events.
- Events include details such as:
  - Name
  - Date and time
  - Location
  - Cost
  - Description
  - Tags (e.g., Workshop, Conference, Meetup)
- Users can search for events by name and register to attend.

### Financial Transactions
- Users can add balance to their accounts.
- Event registration deducts the ticket cost from the user’s balance.
- View transaction history, including all previous completed transactions.

### Secure Sessions
- Sessions managed with Flask-Login.
- MySQL database integration for data storage.
- Input validation and error handling functions built in.

## Tech Stack

- **Backend:** Flask, Flask-SQLAlchemy, Flask-Login
- **Frontend:** HTML, CSS, JavaScript
- **Database:** MySQL
- **Icons:** Google Fonts, Remixicon, Devicon

## Installation

### Prerequisites
- Python 3.7 or higher
- MySQL server
- A virtual environment (recommended)

### Steps to Install and Run

1. **Clone the Repository**
   ```bash
   git clone https://github.com/danielcoblentz/venture.git
   cd venture
   ```
2. **Set up a Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # for windows: ./venv/Scripts/Activate
   ```
3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```
4. **Configure the database**
   - Create a MySQL databse
   - Update the databse URI in `app.py`

5. **start the Application**
   ```bash
   python app.py
   ```