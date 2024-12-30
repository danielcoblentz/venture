from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from decimal import Decimal
from models import db, User, Event, Attendance, Transaction
  #add user & event class from models.py so we can create new users and events
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import stripe

# stripe API keyi -- get from stripe website (search --> developer > API keys)
stripe.api_key = "enter secret key here"
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = "enter DB endpoint+ credentials here"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False

db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# requirements
# define the following base routes --> home, create, transactions, login/signup, acc, about, logout + additional routes as needed
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

    # check creds against DB
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash('invalid email or password.', 'danger')
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

# create route(needs to be an organizer to view page, if user status then dont allow acces! ---------------------------->
@app.route('/create', methods=['GET', 'POST'])
@login_required
def create_event():
    if current_user.role != 'organizer':
        flash("Only organizers can create events.", 'danger')
        return redirect(url_for('home'))

    if request.method == 'POST':
        try:
            # collect form data
            event_name = request.form.get('event_name')
            event_date = request.form.get('event_date')
            end_time = request.form.get('end_time')
            location = request.form.get('event_location')
            cost = request.form.get('event_cost', type=float)
            description = request.form.get('event_description')
            tags = request.form.get('event_tags')

            # Validate inputs
            if not all([event_name, event_date, location, cost]):
                flash("All fields except 'description' are required.", 'danger')
                return redirect(url_for('create_event'))

            # Create and add the event
            new_event = Event(
                organizer_id=current_user.id,
                event_name=event_name,
                event_date=datetime.strptime(event_date, '%Y-%m-%d'),
                end_time=datetime.strptime(end_time, '%Y-%m-%d') if end_time else None,
                location=location,
                cost=Decimal(str(cost)),
                description=description
            )
            db.session.add(new_event)
            db.session.commit()
            flash("Event created successfully!", 'success')
            return redirect(url_for('home'))

        except Exception as e:
            db.session.rollback()
            flash("an error occurred while creating the event.", 'danger')
            return redirect(url_for('create_event'))

    return render_template('layout/create.html')

# route for attending events --------------------------------------------------------------------------------------->
@app.route('/attend-event/<int:event_id>', methods=['POST'])
@login_required
def attend_event(event_id):
    try:
        # get the event
        event = Event.query.get_or_404(event_id)

        # check current user acc balance
        if current_user.balance < Decimal(event.cost):
            flash("insufficient balance.", 'danger')
            return jsonify({"message": "insufficient balance"}), 400

        # deduct balance
        current_user.balance -= Decimal(event.cost)

        # Check if already registered
        existing_attendance = Attendance.query.filter_by(user_id=current_user.id, event_id=event_id).first()
        if existing_attendance:
            flash("you are already registered for this event.", 'danger')
            return jsonify({"message": "already registered"}), 400

        # add current user to attendance record for that event
        attendance = Attendance(user_id=current_user.id, event_id=event_id)
        db.session.add(attendance)

        # Add to current users transaction record
        transaction = Transaction(
            user_id=current_user.id,
            transaction_type='ticket_purchase',
            amount=event.cost,
            event_id=event_id
        )
        db.session.add(transaction)

        db.session.commit()
        flash("successfully registered for the event.", 'success')
        return jsonify({"message": "successfully registered"}), 200

    except Exception as e:
        db.session.rollback()
        print(f"error attending event: {e}")
        return jsonify({"message": "an error occurred"}), 500

# ------------------------------------------------------------------------------------------------------------>
# fetch registered events for current user
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
        return jsonify({"message": "cannot fetch events, try again"}), 500

# ------------------------------------------------------------------------------------------------------------->
# view transaction route (transaction page if no transactions then just render the html page)
@app.route('/transactions')
@login_required
def view_transactions():
    transactions = Transaction.query.filter_by(user_id=current_user.id).all()

    transactions_data = []
    for transaction in transactions:
        event_name = "Account Deposit" if not transaction.event_id else Event.query.get(transaction.event_id).event_name
        formatted_date = transaction.transaction_date.strftime('%b %d')  # display only month and day
        transactions_data.append({
            "event_name": event_name,
            "amount": f"{transaction.amount}",
            "transaction_date": formatted_date,  # formatting date (Month / Day)
        })

    return render_template('layout/transactions.html', transactions=transactions_data)

# ------------------------------------------------------------------------------------------------------------->
# add money to account
@app.route('/add-balance', methods=['POST'])
@login_required
def add_balance():
    try:
        # get the amount from the form
        amount = request.form.get('amount', type=float)

        if not amount or amount <= 0:
            flash('please enter a valid positive amount.', 'danger')
            return redirect(url_for('account'))

        # update curr user balance
        current_user.balance += Decimal(str(amount))

        # create a transaction entry for adding money
        transaction = Transaction(
            user_id=current_user.id,
            transaction_type='add_money',
            amount=Decimal(str(amount)),
            event_id=None
        )
        db.session.add(transaction)
        db.session.commit()

        #message to user after adding currency
        flash(f'your balance has been updated by ${amount:.2f}.', 'success')
        return redirect(url_for('account'))

    except Exception as e:
        db.session.rollback()
        flash('An error happend while processing transaction.', 'danger')
        return redirect(url_for('account'))

# ------------------------------------------------------------------------------------>
#delete event only if that user created that specific event
@app.route('/delete_event/<int:event_id>', methods=['POST'])
@login_required
def delete_event(event_id):
    # get the event by its ID
    event = Event.query.get_or_404(event_id)

    #  current user is the creator of the event?
    if event.organizer_id != current_user.id:
        flash("you do not have permission to delete this event!")
        return redirect(url_for('home'))

    # delete the event
    try:
        db.session.delete(event)
        db.session.commit()
        flash("Event deleted")
    except Exception as e:
        db.session.rollback()
        flash("an error occurred while deleting the event")
    
    return redirect(url_for('home'))

# ------------------------------------------------------------------------------------>
#route for rendering account page
@app.route('/account')
@login_required

def account():
    return render_template('layout/account.html')
# ------------------------------------------------------------------------------------>
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

# ------------------------------------------------------------------------------------>
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
    # ------------------------------------------------------------------------------------>
    # stripe integration for payments (optional -- to use defualt currency method remove hte following functions ("create_payment_intent" & "stripe_webhook"))
@app.route('/create-payment-intent', methods=['POST'])
@login_required
def create_payment_intent():
    try:
        data = request.get_json()
        amount = int(data.get('amount', 0))  # amount should be in cents

        if amount <= 0:
            return jsonify({"error": "Invalid payment amount"}), 400

        # Create a PaymentIntent
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency="usd",
            metadata={"user_id": current_user.id}  # metadata
        )

        return jsonify({"clientSecret": intent['client_secret']})
    except Exception as e:
        return jsonify({"error": "unable to create payment intent"}), 500

# ------------------------------------------------------------------------------------>
@app.route('/stripe-webhook', methods=['POST'])
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, ''
        )
    except ValueError as e:
        print(f"Invalid payload: {e}")
        return jsonify(success=False), 400
    except stripe.error.SignatureVerificationError as e:
        print(f"Invalid signature: {e}")
        return jsonify(success=False), 400

    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        amount = payment_intent['amount'] / 100  # convert cents to dollars
        user_id = payment_intent['metadata']['user_id']

        user = User.query.get(user_id)
        if user:
            user.balance += Decimal(amount)
            db.session.commit()

    return jsonify(success=True), 200

# ------------------------------------------------------------------------------------>
@app.route('/about')
@login_required

def about(): # done no further features needed
    return render_template('layout/about.html')
# ------------------------------------------------------------------------------------>
@app.route('/logout')
@login_required

def logout():
    logout_user()
    flash('you have been logged out')
    return redirect(url_for('login'))
# ------------------------------------------------------------------------------------>
if __name__ == '__main__':
    print("Starting Flask server...")
    app.run(debug=True, port=5000)