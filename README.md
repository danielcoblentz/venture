# venture: Event management system

Venture is a Flask-based web application that allows users to sign up, log in, and manage events. The system supports user authentication, role-based permissions (users & organizers), and event-related functionalities such as creating, reading, updating, and deleting events. This project is integrated with a MySQL database and uses Flask-Login for session management.

## Tech stack
* backend: Flask, Flask-SQLALchemy, Flask-Login
* backend: HTML, CSS, JS
* Database: MySQL
* icons: Google fonts -> icons tab


## Features
* User Authentication:
    - Secure user registration and login using hashed passwords.
    - Role-based user access (user, organizer).

* Event Management:
    - Organizers can perform all necessary CRUD operations and fill out forms for creating events with details such as name, date, location, and cost.
    - users can view and participate in events.

* Database integration:
    - MySQL is used to store user data, event details and transactions.

* Secure sessions:
    - Flask-Login manages user sessions and protects restricted routes.

## Installation

### Prerequisites
    - Python 3.7 or above
    - MySQL server or other database
    - A virtual environment for dependency isolation

### Installation and Setup
1) Clone the Repository: Begin by cloning the repository to your local machine to get all the necessary files:
```
https://github.com/danielcoblentz/venture
```

2) Set up a virtual environment:
```
python -m venv venv
# on mac: source venv/bin/activate  # on windows: venv\Scripts\activate
```

3) Install dependencies:
```
pip install -r requirements.txt
```

4) configure the database:
    - Create a MySQL databse, then update the databse URI in app.py below
    ```
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:<password>@localhost/database_name'
    ```
5) Run the application:
```
python app.py
```
