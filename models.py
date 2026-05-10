from flask_login import UserMixin
from . import db
from datetime import datetime
import enum

class UserRole(enum.Enum):
    CUSTOMER = "Заказчик"
    EXECUTOR = "Исполнитель"

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False)
    balance = db.Column(db.Integer, default=1000)  # стартовый баланс

    tasks_created = db.relationship('Task', foreign_keys='Task.customer_id', backref='customer', lazy=True)
    tasks_taken = db.relationship('Task', foreign_keys='Task.executor_id', backref='executor', lazy=True)

class TaskStatus(enum.Enum):
    OPEN = "Открыта"
    TAKEN = "Принята"
    COMPLETED = "Выполнена"
    VERIFIED = "Подтверждена"

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100))
    reward = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Enum(TaskStatus), default=TaskStatus.OPEN)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    file_path = db.Column(db.String(300))  # прикреплённый файл
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
