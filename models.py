from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# Models
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user')
    balance = db.Column(db.Numeric(10, 2), default=0.00)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    organizer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_name = db.Column(db.String(255), nullable=False)
    event_date = db.Column(db.Date, nullable=False)
    location = db.Column(db.String(255), nullable=False)
    cost = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    description = db.Column(db.Text)
    link = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

class Attendance(db.Model):
    __tablename__ = 'attendance'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    attended_at = db.Column(db.DateTime, default=db.func.now())

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    transaction_type = db.Column(db.Enum('add_money', 'ticket_purchase'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=True)
    transaction_date = db.Column(db.DateTime, default=db.func.now())