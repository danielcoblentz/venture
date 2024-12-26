from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from decimal import Decimal
from models import db, User, Event, Attendance
  #add user & event class from models.py so we can create new users and events
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = None
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False

db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# requirements
# define the following routes --> home, create, transactions, login/signup, acc, about, logout + additional functions for attending events, searching etc..

# home route for redering main page + searching events
@app.route('/')
@login_required

def home():

    # search function to  filter events after entering event name into search bar
    search_query = request.args.get('search', '').strip()
    if search_query:
        events = Event.query.filter(Event.event_name.ilike(f'%{search_query}')).all()
    
    else:
    # if no search query specified then return everything to display on home page
        events = Event.query.all()
    
    return render_template('/layout/home.html', current_user=current_user, events=events)


# register/signup route --------------------------------------------------------------------------------->
@app.route('/register', methods=['GET', 'POST'])

def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = 'organizer' if request.form.get('role') else 'user'

        #check all required fields are filled (username, email, pass)
        if not username or not email or not password:
            flash('fill out all required fields')
            return redirect(url_for('register'))

        # check if email is already registered
        if User.query.filter_by(email=email).first():
            flash('Email already registered -- please login')
            return redirect(url_for('login'))

        # check if username is already in DB
        if User.query.filter_by(username=username).first():
            flash('Username already taken please choose another')
            return redirect(url_for('register'))

        # create a new user after checking the following above
        try:
            new_user = User(username=username, email=email, role=role)
            new_user.set_password(password)  # hash the password
            db.session.add(new_user)
            db.session.commit()
            flash('account created successfully! please login')
            return redirect(url_for('login'))
        
        #if something goes wrong rollback and inform the user
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while creating your account. plz try again.')
            return redirect(url_for('register'))

    # If GET request then just render the signup page as is
    return render_template('layout/signup.html')


# login route ------------------------------------------------------------------------------------------------------>
@app.route('/login', methods=['GET', 'POST'])

def login():
    # get the submitted (email, pass) from input form
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

    # check credentials
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash('Invalid email or password.', 'danger')
            return redirect(url_for('login'))

        login_user(user)
        return redirect(url_for('home'))
    return render_template('layout/login.html')


# event_details route for displaying content on home page & for preview pannel details ----------------------------->
@app.route('/event-details/<int:event_id>')
@login_required

def event_details(event_id):
    event = Event.query.get_or_404(event_id)
    return {
        "event_name": event.event_name,
        "event_date": event.event_date,
        "location": event.location,
        "cost": event.cost,
        "description": event.description
    }

# create route(needs to be an organizer to view page, if user status then dont allow acces ---------------------------->

@app.route('/create', methods=['GET', 'POST'])
@login_required

def create_event():
    # check if current_user is an organizer
    if current_user.role != 'organizer':
        flash('you do not have permission to create events, you may only attend them')
        return redirect(url_for('home')) # redirect them back to home if user permissions are active
    

    # if organizer then collect event info to be inserted
    if request.method == 'POST':
        event_name = request.form.get('event_name')
        event_link = request.form.get('event_link')
        event_date = request.form.get('event_date')
        event_location = request.form.get('event_location')
        event_cost = request.form.get('event_cost')
        event_description = request.form.get('event_description')
        event_tags = request.form.get('event_tags')

        # validate input fields
        if not event_name or not event_date or not event_location or not event_cost:
            return redirect(url_for('create_event'))

        # create event and add to DB
        try:
            new_event = Event (
                organizer_id=current_user.id,
                event_name=event_name,
                event_date=event_date,
                location=event_location,
                cost=event_cost,
                description=event_description,
                link=event_link
            )

            db.session.add(new_event)
            db.session.commit()

            # after inserting event send confirmation message
            flash('event created successfully!')
            return redirect(url_for('home'))
        
        # if an error occurs then rollback
        except Exception as e:
            db.session.rollback()
            flash('an error occurred while creating the event, please try again.')
            return redirect(url_for('create_event'))

    #if a GET request and user is organizer, show the create event page
    return render_template('layout/create.html')

# route for attending events --------------------------------------------------------------------------------------->
@app.route('/attend-event/<int:event_id>', methods=['POST'])
@login_required
def attend_event(event_id):
    try:
        # Fetch event details
        event = Event.query.get_or_404(event_id)

        # Check if user has sufficient balance
        if current_user.balance < event.cost:
            return jsonify({"message": "Insufficient balance"}), 400

        # Deduct the balance
        current_user.balance -= event.cost

        # Check if the user is already attending the event
        existing_attendance = Attendance.query.filter_by(user_id=current_user.id, event_id=event_id).first()
        if existing_attendance:
            return jsonify({"message": "You are already registered for this event"}), 400

        # add attendance record
        attendance = Attendance(user_id=current_user.id, event_id=event_id)
        db.session.add(attendance)

        # commit changes to DB
        db.session.commit()
        return jsonify({"message": "Successfully registered"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "An error occurred"}), 500

# ------------------------------------------------------------------------------------------------------------>
# fetch registered events
@app.route('/my-events', methods=['GET'])
@login_required
def my_events():
    try:
        # query all events the user is registered for from DB
        events = Event.query.join(Attendance, Attendance.event_id == Event.id)\
            .filter(Attendance.user_id == current_user.id).all()

        # events for the frontend
        events_data = [{
            "id": event.id,
            "name": event.event_name,
            "date": event.event_date.strftime('%Y-%m-%d'),
            "location": event.location,
            "cost": str(event.cost),
            "description": event.description,
        } for event in events]

        return jsonify(events_data), 200
    except Exception as e:
        return jsonify({"message": "Failed to fetch events"}), 500

# ------------------------------------------------------------------------------------------------------------->

# other routes will add logic soon
@app.route('/transactions')
@login_required

def view_transactions():
    return render_template('layout/transactions.html')

# add money to account
@app.route('/add-balance', methods=['POST'])
@login_required
def add_balance():
    try:
        # get the amount and convert it to Decimal
        amount = request.form.get('amount', type=float)

        if not amount or amount <= 0:
            flash(' enter a valid positive amount.', 'danger')
            return redirect(url_for('account'))

        current_user.balance += Decimal(str(amount))  

        db.session.commit()# update message
        flash(f'your balance has been updated by ${amount:.2f}.', 'success')

    except Exception as e:
        db.session.rollback()

    return redirect(url_for('account'))


@app.route('/account')
@login_required

def account():
    return render_template('layout/account.html')

# update email route (account page)
@app.route('/update-email', methods=['POST'])
@login_required
def update_email():
    try:
        data = request.get_json()
        new_email = data.get('email')

        if not new_email:
            return jsonify({"message": "email is required"}), 400

        # update the email in the database
        current_user.email = new_email
        db.session.commit()

        return jsonify({"message": "email updated! you should see the change above"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "error occurred"}), 500


# update password route (account page)
@app.route('/update-password', methods=['POST'])
@login_required
def update_password():
    try:
        data = request.get_json()
        new_password = data.get('new_password')
        current_password = data.get('current_password')

        if not new_password or not current_password:
            return jsonify({"message": "all fields are required"}), 400

        # verify current password
        if not current_user.check_password(current_password):
            return jsonify({"message": "current password is incorrect"}), 400

        # update the password
        current_user.password = generate_password_hash(new_password)
        db.session.commit()

        return jsonify({"message": "password updated!"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "error"}), 500

@app.route('/about')
@login_required

def about(): # done no further features needed
    return render_template('layout/about.html')

@app.route('/logout')
@login_required

def logout():
    logout_user()
    flash('you have been logged out')
    return redirect(url_for('login'))

if __name__ == '__main__':
    print("Starting Flask server...")
    app.run(debug=True, port=5000)
