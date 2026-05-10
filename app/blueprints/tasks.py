from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from .. import db
from ..models import Task, TaskStatus, User, UserRole, Message
from ..forms import TaskForm
from ..utils import generate_ai_description
from flask import send_from_directory

tasks_bp = Blueprint('tasks', __name__)


# ====================== ОСНОВНЫЕ ФУНКЦИИ ======================
@tasks_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if current_user.role != UserRole.CUSTOMER:
        flash('Только заказчики могут создавать задачи', 'danger')
        return redirect(url_for('main.dashboard'))

    form = TaskForm()
    if form.validate_on_submit():
        task = Task(
            title=form.title.data,
            description=form.description.data,
            category=form.category.data,
            reward=form.reward.data,
            customer_id=current_user.id
        )
        if current_user.balance >= form.reward.data:
            current_user.balance -= form.reward.data
        else:
            flash('Недостаточно баллов!', 'danger')
            return render_template('create_task.html', form=form)

        db.session.add(task)
        db.session.commit()
        flash('Задача создана!', 'success')
        return redirect(url_for('tasks.list_tasks'))

    return render_template('create_task.html', form=form)


@tasks_bp.route('/list')
def list_tasks():
    tasks = Task.query.filter(
        Task.status.in_([TaskStatus.OPEN, TaskStatus.TAKEN])
    ).order_by(Task.created_at.desc()).all()
    return render_template('task_list.html', tasks=tasks)


@tasks_bp.route('/<int:task_id>')
def task_detail(task_id):
    task = Task.query.get_or_404(task_id)
    messages = Message.query.filter_by(task_id=task_id)\
        .order_by(Message.created_at.asc()).all()
    return render_template('task_detail.html', task=task, messages=messages)


# ====================== ЧАТ ======================
@tasks_bp.route('/<int:task_id>/send_message', methods=['POST'])
@login_required
def send_message(task_id):
    task = Task.query.get_or_404(task_id)
    if current_user.id not in [task.customer_id, task.executor_id]:
        flash('Вы не участник этой задачи', 'danger')
        return redirect(url_for('tasks.task_detail', task_id=task_id))

    text = request.form.get('text', '').strip()
    if not text:
        flash('Сообщение не может быть пустым', 'danger')
        return redirect(url_for('tasks.task_detail', task_id=task_id))

    message = Message(task_id=task_id, sender_id=current_user.id, text=text)
    db.session.add(message)
    db.session.commit()

    flash('Сообщение отправлено', 'success')
    return redirect(url_for('tasks.task_detail', task_id=task_id))


# ====================== АДМИН ФУНКЦИИ ======================
@tasks_bp.route('/<int:task_id>/cancel')
@login_required
def cancel_task(task_id):
    task = Task.query.get_or_404(task_id)
    
    if current_user.role != UserRole.ADMIN:
        flash('Только администратор может отменять задачи', 'danger')
        return redirect(url_for('tasks.task_detail', task_id=task_id))

    if task.status == TaskStatus.CANCELLED:
        flash('Задача уже отменена', 'warning')
        return redirect(url_for('tasks.task_detail', task_id=task_id))

    # Возврат денег заказчику
    customer = User.query.get(task.customer_id)
    if customer:
        customer.balance += task.reward

    task.status = TaskStatus.CANCELLED
    db.session.commit()

    flash('Задача отменена. Деньги возвращены заказчику.', 'success')
    return redirect(url_for('tasks.task_detail', task_id=task_id))


# Скачивание файлов (на всякий случай оставляем)
@tasks_bp.route('/uploads/<filename>')
def download_file(filename):
    return send_from_directory('uploads', filename)
