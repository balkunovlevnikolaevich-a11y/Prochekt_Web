from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from .. import db
from ..models import Task, TaskStatus, User, UserRole, Message   # ← исправленный импорт
from ..forms import TaskForm
from ..utils import generate_ai_description

tasks_bp = Blueprint('tasks', __name__)


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
    # Показываем только активные задачи (Открыта и Принята)
    # Завершённые (Выполнена и Подтверждена) больше не отображаются в общем списке
    tasks = Task.query.filter(
        Task.status.in_([TaskStatus.OPEN, TaskStatus.TAKEN])
    ).order_by(Task.created_at.desc()).all()
    
    return render_template('task_list.html', tasks=tasks)

@tasks_bp.route('/<int:task_id>')
def task_detail(task_id):
    task = Task.query.get_or_404(task_id)
    
    # Загружаем все сообщения по задаче
    messages = Message.query.filter_by(task_id=task_id)\
        .order_by(Message.created_at.asc()).all()
    
    return render_template('task_detail.html', task=task, messages=messages)

@tasks_bp.route('/<int:task_id>/take')
@login_required
def take_task(task_id):
    task = Task.query.get_or_404(task_id)
    
    print(f"DEBUG: Задача {task.id} | Статус: {task.status} | Исполнитель: {task.executor_id}")

    if task.status != TaskStatus.OPEN:          # ← используем Enum, а не .value
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


@tasks_bp.route('/<int:task_id>/complete')
@login_required
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)
    
    if task.executor_id != current_user.id:
        flash('Это не ваша задача', 'danger')
        return redirect(url_for('tasks.task_detail', task_id=task_id))
    
    # Исполнитель только отмечает как выполненную (ожидает подтверждения)
    task.status = TaskStatus.COMPLETED
    db.session.commit()
    
    flash('Задача отмечена как выполненная. Ожидаем подтверждения заказчика.', 'success')
    return redirect(url_for('tasks.task_detail', task_id=task_id))
    
@tasks_bp.route('/ai_generate', methods=['POST'])
@login_required
def ai_generate():
    prompt = request.form.get('prompt', '')
    description = generate_ai_description(prompt)
    return {'description': description}  # для JS (можно расширить)
    
@tasks_bp.route('/<int:task_id>/confirm')
@login_required
def confirm_task(task_id):
    task = Task.query.get_or_404(task_id)
    
    # Только заказчик может подтвердить
    if task.customer_id != current_user.id:
        flash('Только заказчик может подтвердить выполнение', 'danger')
        return redirect(url_for('tasks.task_detail', task_id=task_id))
    
    if task.status != TaskStatus.COMPLETED:
        flash('Задача ещё не отмечена как выполненная', 'danger')
        return redirect(url_for('tasks.task_detail', task_id=task_id))
    
    # Подтверждаем выполнение
    task.status = TaskStatus.VERIFIED
    
    # Начисляем деньги исполнителю
    executor = User.query.get(task.executor_id)
    if executor:
        executor.balance += task.reward
    
    db.session.commit()
    
    flash('Выполнение подтверждено! Деньги перечислены исполнителю.', 'success')
    return redirect(url_for('tasks.task_detail', task_id=task_id))

# ====================== ЧАТ ======================
@tasks_bp.route('/<int:task_id>/send_message', methods=['POST'])
@login_required
def send_message(task_id):
    task = Task.query.get_or_404(task_id)
    
    # Только участники задачи могут писать
    if current_user.id not in [task.customer_id, task.executor_id]:
        flash('Вы не участник этой задачи', 'danger')
        return redirect(url_for('tasks.task_detail', task_id=task_id))

    text = request.form.get('text', '').strip()
    file = request.files.get('file')

    if not text and not file:
        flash('Сообщение не может быть пустым', 'danger')
        return redirect(url_for('tasks.task_detail', task_id=task_id))

    message = Message(task_id=task_id, sender_id=current_user.id, text=text)

    if file and file.filename:
        filename = secure_filename(file.filename)
        file_path = os.path.join('uploads', filename)
        file.save(file_path)
        message.file_path = file_path

    db.session.add(message)
    db.session.commit()

    flash('Сообщение отправлено', 'success')
    return redirect(url_for('tasks.task_detail', task_id=task_id))
