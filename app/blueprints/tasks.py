from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from .. import db
from ..models import Task, TaskStatus, User, UserRole, Message
from ..forms import TaskForm
from ..utils import generate_ai_description

tasks_bp = Blueprint('tasks', __name__)


# Создание задачи
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


# Список задач
@tasks_bp.route('/list')
def list_tasks():
    tasks = Task.query.filter(
        Task.status.in_([TaskStatus.OPEN, TaskStatus.TAKEN])
    ).order_by(Task.created_at.desc()).all()
    return render_template('task_list.html', tasks=tasks)


# Детали задачи
@tasks_bp.route('/<int:task_id>')
def task_detail(task_id):
    task = Task.query.get_or_404(task_id)
    messages = Message.query.filter_by(task_id=task_id).order_by(Message.created_at.asc()).all()
    return render_template('task_detail.html', task=task, messages=messages)


# Взять задачу
@tasks_bp.route('/<int:task_id>/take')
@login_required
def take_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.status != TaskStatus.OPEN:
        flash('Задача уже занята или завершена', 'danger')
        return redirect(url_for('tasks.task_detail', task_id=task_id))
    if task.customer_id == current_user.id:
        flash('Вы не можете взять свою собственную задачу', 'danger')
        return redirect(url_for('tasks.task_detail', task_id=task_id))

    task.status = TaskStatus.TAKEN
    task.executor_id = current_user.id
    db.session.commit()
    flash('Задача успешно взята в работу! ✅', 'success')
    return redirect(url_for('tasks.task_detail', task_id=task_id))


# Отметить как выполненную
@tasks_bp.route('/<int:task_id>/complete')
@login_required
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.executor_id != current_user.id:
        flash('Это не ваша задача', 'danger')
        return redirect(url_for('tasks.task_detail', task_id=task_id))

    task.status = TaskStatus.COMPLETED
    db.session.commit()
    flash('Задача отмечена как выполненная. Ожидаем подтверждения.', 'success')
    return redirect(url_for('tasks.task_detail', task_id=task_id))


# Подтвердить выполнение
@tasks_bp.route('/<int:task_id>/confirm')
@login_required
def confirm_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.customer_id != current_user.id:
        flash('Только заказчик может подтвердить', 'danger')
        return redirect(url_for('tasks.task_detail', task_id=task_id))

    if task.status != TaskStatus.COMPLETED:
        flash('Задача ещё не отмечена как выполненная', 'danger')
        return redirect(url_for('tasks.task_detail', task_id=task_id))

    task.status = TaskStatus.VERIFIED
    executor = User.query.get(task.executor_id)
    if executor:
        executor.balance += task.reward

    db.session.commit()
    flash('Выполнение подтверждено! Деньги перечислены.', 'success')
    return redirect(url_for('tasks.task_detail', task_id=task_id))


# Чат
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


# Отмена задачи (только админ)
@tasks_bp.route('/<int:task_id>/cancel')
@login_required
def cancel_task(task_id):
    task = Task.query.get_or_404(task_id)
    if current_user.role != UserRole.ADMIN:
        flash('Только администратор может отменять задачи', 'danger')
        return redirect(url_for('tasks.task_detail', task_id=task_id))

    customer = User.query.get(task.customer_id)
    if customer:
        customer.balance += task.reward

    task.status = TaskStatus.CANCELLED
    db.session.commit()
    flash('Задача отменена. Деньги возвращены заказчику.', 'success')
    return redirect(url_for('tasks.task_detail', task_id=task_id))
