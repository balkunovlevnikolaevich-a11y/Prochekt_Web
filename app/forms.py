from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, IntegerField
from wtforms.validators import DataRequired, Length, NumberRange

class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6)])
    role = SelectField('Роль', choices=[('CUSTOMER', 'Заказчик'), ('EXECUTOR', 'Исполнитель')], validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')

class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')

class TaskForm(FlaskForm):
    title = StringField('Название задачи', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Описание', validators=[DataRequired()])
    category = StringField('Категория')
    reward = IntegerField('Награда (баллы)', validators=[DataRequired(), NumberRange(min=10)])
    file = FileField('Прикрепить файл', validators=[FileAllowed(['png', 'jpg', 'jpeg', 'pdf', 'doc', 'docx'])])
    submit = SubmitField('Создать задачу')
