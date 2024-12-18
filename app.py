# import libraries for flask and session management
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import current_user


#initialize flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# define database
db = SQLAlchemy(app)


#initialize flask-login
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# define the user model
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# load user for flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#---------------------------------------------------------------------------------------- routes for loading each page and handling data
# routes: --> home, register, login, create, transaction, account, about, logout


# home Route (requires login) -- routes user to home.html
@app.route('/')
@login_required
def home():
    return render_template('/layout/home.html', current_user = current_user)

# signup route -- insert new user credentials into db
@app.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('layout/signup.html')

# login route -- valdiate creds from db
@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('layout/login.html')


# create route -- insert new events (only if organizer is applied)
@app.route('/create')
@login_required
def create():
    return render_template('layout/create.html')


# transaction route -- show currency and purchased tickets/confirmation
@app.route('/transactions')
@login_required
def create():
    return render_template('layout/transacrtions.html')


# account route -- display and update account info (email,pass, potentially add currency here)
@app.route('/account')
@login_required
def create():
    return render_template('layout/account.html')


# about route -- just to render the page 
@app.route('/about')
@login_required
def create():
    return render_template('layout/about.html')



#logout route exit the web app
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('you have been logged out')
    return redirect(url_for('login'))



# run the application + debugging rn
if __name__ == '__main__':
    with app.app_context():
        # create database tables if they don't exist
        db.create_all()
        print("Database tables created successfully.")
    print("Starting Flask server...")
    app.run(debug=True, port=5000)
