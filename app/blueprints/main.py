from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from .. import db   # ← добавили

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    # Принудительно обновляем пользователя из базы при каждом заходе
    db.session.refresh(current_user)
    return render_template('dashboard.html')
