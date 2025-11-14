from app import db
from flask_login import UserMixin

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.Text, nullable=False)
    users = db.relationship('User', back_populates='role')

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(64), nullable=False, unique=True)
    password_hash = db.Column(db.String(512), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    first_name = db.Column(db.String(64), nullable=False)
    middle_name = db.Column(db.String(64))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    role = db.relationship('Role', back_populates='users')
    organized = db.relationship('Event', back_populates='organizer', cascade='all, delete')
    registrations = db.relationship('Registration', back_populates='volunteer', cascade='all, delete')

class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.Date, nullable=False)
    place = db.Column(db.String(128), nullable=False)
    volunteers_required = db.Column(db.Integer, nullable=False)
    image_filename = db.Column(db.String(255), nullable=False)
    organizer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    organizer = db.relationship('User', back_populates='organized')
    registrations = db.relationship('Registration', back_populates='event', cascade='all, delete')

class Registration(db.Model):
    __tablename__ = 'registrations'
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    volunteer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    contact_info = db.Column(db.String(255), nullable=False)
    registered_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    status = db.Column(db.String(16), nullable=False, default='pending')
    event = db.relationship('Event', back_populates='registrations')
    volunteer = db.relationship('User', back_populates='registrations')
