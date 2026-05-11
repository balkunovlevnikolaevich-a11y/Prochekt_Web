from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .. import db
from ..models import User, UserRole
from ..forms import RegistrationForm, LoginForm

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()   # ← нужно для красивого шаблона

    if form.validate_on_submit():
        username = form.username.data.strip()

        # ←←←←←←←←←←←←←←←←← АВТОМАТИЧЕСКАЯ ВЫДАЧА АДМИНА ←←←←←←←←←←←←←←←←←
        if username.lower() == 'admin':
            role = UserRole.ADMIN
        else:
            role = form.role.data
        # ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←

        # Проверка на существование пользователя
        if User.query.filter_by(username=username).first():
            flash('Пользователь с таким именем уже существует!', 'danger')
            return redirect(url_for('auth.register'))

        user = User(
            username=username,
            role=role,
            balance=1000
        )
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        flash('Регистрация прошла успешно! Теперь войдите в аккаунт.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Вы успешно вошли!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Неверный логин или пароль', 'danger')
    return render_template('login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из аккаунта', 'info')
    return redirect(url_for('main.index'))
