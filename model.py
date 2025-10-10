from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date
from enum import Enum

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(100))
    email = db.Column(db.String(255), unique=True, nullable=False)
    _password = db.Column('password', db.String(100), nullable=False)
    status = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.Date, default=date.today)
    updated_at = db.Column(db.Date, default=date.today, onupdate=date.today)
    tasks = db.relationship('Task', backref='user', cascade="all, delete-orphan")

    @property
    def password(self):
        raise AttributeError("Password is not readable.")

    @password.setter
    def password(self, plain_text_password):
        self._password = generate_password_hash(plain_text_password)

    def check_password(self, password):
        return check_password_hash(self._password, password)
        
        
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500))
    priority = db.Column(db.Enum('low', 'medium', 'high', name='priority_levels'), default='medium')
    due_date = db.Column(db.Date)
    status = db.Column(db.Enum('pending', 'completed', name='task_status'), default='pending')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.Date, default=date.today)
    updated_at = db.Column(db.Date, default=date.today, onupdate=date.today)


class PriorityLevel(Enum):
        LOW = "low"
        MEDIUM = "medium"
        HIGH = "high"
        
class TaskStatus(Enum):
        PENDING = "pending"
        COMPLETED = "completed"