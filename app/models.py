from flask_login import UserMixin
from . import db
from datetime import datetime
import enum
from werkzeug.security import generate_password_hash, check_password_hash


class UserRole(enum.Enum):
    CUSTOMER = "Заказчик"
    EXECUTOR = "Исполнитель"


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False)
    balance = db.Column(db.Integer, default=1000)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

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
    category = db.Column(db.String(100), nullable=True)
    reward = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Enum(TaskStatus), default=TaskStatus.OPEN)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # Изменено: теперь храним только имя файла, а не путь
    file_name = db.Column(db.String(300), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Связь с сообщениями чата
    messages = db.relationship('Message', backref='task', lazy=True, cascade="all, delete-orphan")


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    text = db.Column(db.Text, nullable=True)
    
    # Изменено: теперь храним только имя файла
    file_name = db.Column(db.String(300), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')

    def __repr__(self):
        return f'<Message {self.id}>'
