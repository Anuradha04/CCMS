from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'student', 'board', 'dsw'
    
    # Relations
    clubs = db.relationship('ClubMember', back_populates='user')
    registrations = db.relationship('Registration', back_populates='user')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    venue = db.Column(db.String(100), nullable=False)
    date_from = db.Column(db.Date, nullable=False)
    date_to = db.Column(db.Date, nullable=False)
    time_from = db.Column(db.Time, nullable=False)
    time_to = db.Column(db.Time, nullable=False)
    poc = db.Column(db.String(100), nullable=False)  # Point of Contact
    
    # Foreign Keys
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relations
    club = db.relationship('Club', back_populates='events')
    creator = db.relationship('User')
    registrations = db.relationship('Registration', back_populates='event', cascade="all, delete-orphan")
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Club(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'club' or 'chapter'
    description = db.Column(db.Text, nullable=False)
    
    # Relations
    members = db.relationship('ClubMember', back_populates='club', cascade="all, delete-orphan")
    events = db.relationship('Event', back_populates='club', cascade="all, delete-orphan")
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ClubMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    position = db.Column(db.String(50), nullable=False)  # chairperson, vice chairperson, secretary, co-secretary, member
    
    # Relations
    club = db.relationship('Club', back_populates='members')
    user = db.relationship('User', back_populates='clubs')
    
    __table_args__ = (db.UniqueConstraint('club_id', 'user_id', name='unique_club_member'),)

class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    
    # Relations
    user = db.relationship('User', back_populates='registrations')
    event = db.relationship('Event', back_populates='registrations')
    
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'event_id', name='unique_registration'),)
