from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, User, Event  #add user & event class from models.py so we can create new users and events
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = None
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#enabled echo to see SQL statements in the terminal (in pain debugging rn)
app.config['SQLALCHEMY_ECHO'] = True

db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#create the tables if they don't exist print to terminal
with app.app_context():
    db.create_all()
    print("DB tables created successfully")
# define the following routes --> home, create, transactions, login/signup, acc, about, logout

# home route for main page
@app.route('/')
@login_required
def home():
    return render_template('/layout/home.html', current_user=current_user)


# register/signup route -->
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = 'organizer' if request.form.get('role') else 'user'

        print(f"Username: {username}, Email: {email}, Password: {password}, Role: {role}")

        #check all required fields are filled (username, email, pass)
        if not username or not email or not password:
            flash('please fill out all required fields.')
            return redirect(url_for('register'))

        # check if email is already registered
        if User.query.filter_by(email=email).first():
            flash('Email already registered. Please login.')
            return redirect(url_for('login'))

        # check if username is taken
        if User.query.filter_by(username=username).first():
            flash('Username already taken. Please choose another.')
            return redirect(url_for('register'))

        # create a new user if we can
        try:
            new_user = User(username=username, email=email, role=role)
            new_user.set_password(password)  # hash the password
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully! Please login.')
            return redirect(url_for('login'))
        
        except Exception as e:
            #if something goes wrong rollback and inform the user
            db.session.rollback()
            flash('An error occurred while creating your account. plz try again.')
            return redirect(url_for('register'))

    # If GET request then just render the signup page as is
    return render_template('layout/signup.html')

# login route -->
@app.route('/login', methods=['GET', 'POST'])
def login():
    # get the submitted email, pass from form
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

# create route(needs to be an organizer to view page NOT user) -->

@app.route('/create', methods=['GET', 'POST'])
@login_required
def create_event():
    # check if current_user is an organizer
    if current_user.role != 'organizer':
        flash('you do not have permission to create events, you may only attend them')
        return redirect(url_for('home')) # redirect them back to home if user permissions are active
    # if organizer then collect event info 
    if request.method == 'POST':
        event_name = request.form.get('event_name')
        event_link = request.form.get('event_link')
        event_date = request.form.get('event_date')
        event_location = request.form.get('event_location')
        event_cost = request.form.get('event_cost')
        event_description = request.form.get('event_description')
        event_tags = request.form.get('event_tags')

        # validate required fields
        if not event_name or not event_date or not event_location or not event_cost:
            flash('Please fill out all required fields.')
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
                # need to do tags
            )
            db.session.add(new_event)
            db.session.commit()
            # after inserting event send message to user
            flash('event created successfully!')
            return redirect(url_for('home'))
        except Exception as e:
            db.session.rollback()
            flash('an error occurred while creating the event, please try again.')
            return redirect(url_for('create_event'))

    #if a GET request and user is organizer, show the create event page
    return render_template('layout/create.html')

@app.route('/transactions')
@login_required
def view_transactions():
    return render_template('layout/transactions.html')

@app.route('/account')
@login_required
def account():
    return render_template('layout/account.html')

@app.route('/about')
@login_required
def about():
    return render_template('layout/about.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out')
    return redirect(url_for('login'))

if __name__ == '__main__':
    print("Starting Flask server...")
    app.run(debug=True, port=5000)
