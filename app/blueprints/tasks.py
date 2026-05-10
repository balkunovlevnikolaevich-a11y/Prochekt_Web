from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from .. import db
from ..models import Task, User
from ..forms import TaskForm
from ..utils import generate_ai_description

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if current_user.role != 'CUSTOMER':
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
        # Списание награды
        if current_user.balance >= form.reward.data:
            current_user.balance -= form.reward.data
        else:
            flash('Недостаточно баллов!', 'danger')
            return render_template('create_task.html', form=form)

        # Загрузка файла
        if form.file.data:
            file = form.file.data
            filename = secure_filename(file.filename)
            file_path = os.path.join('uploads', filename)
            file.save(file_path)
            task.file_path = file_path

        db.session.add(task)
        db.session.commit()
        flash('Задача создана!', 'success')
        return redirect(url_for('tasks.list_tasks'))
    
    return render_template('create_task.html', form=form)

@tasks_bp.route('/list')
def list_tasks():
    tasks = Task.query.filter_by(status='Открыта').all()
    return render_template('task_list.html', tasks=tasks)

@tasks_bp.route('/<int:task_id>')
def task_detail(task_id):
    task = Task.query.get_or_404(task_id)
    return render_template('task_detail.html', task=task)

@tasks_bp.route('/<int:task_id>/take')
@login_required
def take_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.status != 'Открыта':
        flash('Задача уже занята', 'danger')
        return redirect(url_for('tasks.task_detail', task_id=task_id))
    
    task.status = 'Принята'
    task.executor_id = current_user.id
    db.session.commit()
    flash('Задача принята!', 'success')
    return redirect(url_for('tasks.task_detail', task_id=task_id))

@tasks_bp.route('/<int:task_id>/complete')
@login_required
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.executor_id != current_user.id:
        flash('Это не ваша задача', 'danger')
        return redirect(url_for('tasks.task_detail', task_id=task_id))
    
    task.status = 'Выполнена'
    db.session.commit()
    flash('Задача отмечена как выполненная!', 'success')
    return redirect(url_for('tasks.task_detail', task_id=task_id))

@tasks_bp.route('/ai_generate', methods=['POST'])
@login_required
def ai_generate():
    prompt = request.form.get('prompt', '')
    description = generate_ai_description(prompt)
    return {'description': description}  # для JS (можно расширить)
