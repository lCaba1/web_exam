from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import func
from werkzeug.utils import secure_filename
import os
import bleach
import markdown

from app import db
from app.models import Event, User, Registration, Role
from app.forms import LoginForm, EventForm
from werkzeug.security import check_password_hash

# Разрешенные теги для Markdown
ALLOWED_TAGS = bleach.sanitizer.ALLOWED_TAGS.union(
    {'p', 'pre', 'h1', 'h2', 'h3', 'ul', 'ol', 'li', 'strong', 'em', 'a'}
)

main_bp = Blueprint('main', __name__)

def get_accepted_count(event):
    """Подсчет принятых волонтеров для мероприятия"""
    return Registration.query.filter_by(event_id=event.id, status='accepted').count()

@main_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    pagination = Event.query \
        .filter(Event.date >= func.current_date()) \
        .order_by(Event.date.asc()) \
        .paginate(page=page, per_page=9, error_out=False)
    events = pagination.items
    return render_template('index.html',
                           events=events,
                           pagination=pagination,
                           get_accepted_count=get_accepted_count)

@main_bp.route('/event/create', methods=['GET', 'POST'])
@login_required
def create_event():
    if current_user.role.name != 'admin':
        flash('У вас недостаточно прав для создания мероприятия', 'danger')
        return redirect(url_for('main.index'))

    form = EventForm()

    if form.validate_on_submit():
        try:
            # Убедимся, что папка uploads существует
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)

            # Сохраняем файл
            filename = secure_filename(form.image.data.filename)
            filepath = os.path.join(upload_folder, filename)
            form.image.data.save(filepath)

            # Санитизируем описание
            desc_html = bleach.clean(
                form.description.data,
                tags=ALLOWED_TAGS,
                strip=True
            )

            # Создаём запись в БД
            ev = Event(
                name=form.name.data,
                description=desc_html,
                date=form.date.data,
                place=form.place.data,
                volunteers_required=form.volunteers_required.data,
                image_filename=filename,
                organizer_id=current_user.id
            )
            db.session.add(ev)
            db.session.commit()

            flash('Мероприятие успешно создано!', 'success')
            return redirect(url_for('main.event_detail', event_id=ev.id))

        except Exception as e:
            db.session.rollback()
            flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')

    elif request.method == 'POST':
        flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')

    return render_template('event_create.html', form=form)


@main_bp.route('/event/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)

    if current_user.role.name not in ['admin', 'moderator']:
        flash('Недостаточно прав для редактирования', 'danger')
        return redirect(url_for('main.index'))

    form = EventForm(obj=event)

    if form.validate_on_submit():
        # Обновляем данные из формы, кроме изображения
        event.name = form.name.data
        event.date = form.date.data
        event.place = form.place.data
        event.volunteers_required = form.volunteers_required.data

        # Санитизируем описание
        event.description = bleach.clean(
            form.description.data,
            tags=ALLOWED_TAGS,
            strip=True
        )

        try:
            db.session.commit()
            flash('Мероприятие успешно обновлено!', 'success')
            return redirect(url_for('main.event_detail', event_id=event.id))
        except Exception as e:
            db.session.rollback()
            flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')
    elif request.method == 'POST':
        # Форма не прошла валидацию
        flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')

    return render_template('event_edit.html', form=form, event=event)


@main_bp.route('/event/<int:event_id>/delete', methods=['POST'])
@login_required
def delete_event(event_id):
    ev = Event.query.get_or_404(event_id)
    if current_user.role.name != 'admin':
        abort(403)
    db.session.delete(ev)
    db.session.commit()
    flash('Мероприятие удалено', 'success')
    return redirect(url_for('main.index'))

@main_bp.route('/event/<int:event_id>')
def event_detail(event_id):
    ev = Event.query.get_or_404(event_id)
    
    # Получаем заявку текущего пользователя (если он авторизован)
    user_registration = None
    if current_user.is_authenticated:
        user_registration = Registration.query.filter_by(
            event_id=event_id, 
            volunteer_id=current_user.id
        ).first()
    
    # Получаем списки заявок по статусам
    accepted_registrations = Registration.query.filter_by(
        event_id=event_id, status='accepted'
    ).all()
    pending_registrations = Registration.query.filter_by(
        event_id=event_id, status='pending'
    ).all()
    
    # Подсчёт подтверждённых заявок
    accepted_count = Registration.query.filter_by(
        event_id=event_id, status='accepted'
    ).count()

    # Преобразуем Markdown-описание в HTML
    html_description = markdown.markdown(ev.description)

    return render_template(
        'event_detail.html', 
        event=ev,
        html_description=html_description,
        accepted_registrations=accepted_registrations,
        pending_registrations=pending_registrations,
        accepted_count=accepted_count,
        user_registration=user_registration
    )

@main_bp.route('/event/<int:event_id>/register', methods=['POST'])
@login_required
def register(event_id):
    ev = Event.query.get_or_404(event_id)

    if current_user.role.name in ['admin', 'moderator']:
        flash('Администраторы и модераторы не могут регистрироваться на мероприятия', 'warning')
        return redirect(url_for('main.event_detail', event_id=event_id))
    
    # Проверяем, не зарегистрирован ли уже пользователь
    existing_reg = Registration.query.filter_by(
        event_id=event_id, 
        volunteer_id=current_user.id
    ).first()
    
    if existing_reg:
        flash('Вы уже подали заявку на это мероприятие', 'warning')
        return redirect(url_for('main.event_detail', event_id=event_id))
    
    # Проверяем, есть ли еще свободные места
    accepted_count = Registration.query.filter_by(event_id=event_id, status='accepted').count()
    if accepted_count >= ev.volunteers_required:
        flash('На это мероприятие уже набрано достаточное количество волонтёров', 'danger')
        return redirect(url_for('main.event_detail', event_id=event_id))
    
    contact = request.form.get('contact_info', '').strip()
    if not contact:
        flash('Укажите контактную информацию', 'danger')
        return redirect(url_for('main.event_detail', event_id=event_id))
    
    # Создаем заявку
    reg = Registration(
        event_id=ev.id,
        volunteer_id=current_user.id,
        contact_info=contact,
        status='pending'  # по умолчанию
    )
    db.session.add(reg)
    db.session.commit()
    flash('Ваша заявка отправлена на модерацию', 'success')
    return redirect(url_for('main.event_detail', event_id=event_id))

@main_bp.route('/registration/<int:reg_id>/accept')
@login_required
def accept_registration(reg_id):
    reg = Registration.query.get_or_404(reg_id)
    if current_user.role.name not in ('admin', 'moderator'):
        abort(403)
    
    # Проверяем, не превысит ли это количество волонтеров
    event = reg.event
    accepted_count = Registration.query.filter_by(event_id=event.id, status='accepted').count()
    if accepted_count >= event.volunteers_required:
        flash('Невозможно принять заявку: превышено количество волонтёров', 'danger')
        return redirect(url_for('main.event_detail', event_id=event.id))
    
    reg.status = 'accepted'
    db.session.commit()
    
    # Проверяем, не заполнилась ли квота
    new_accepted_count = accepted_count + 1
    if new_accepted_count >= event.volunteers_required:
        # Отклоняем все оставшиеся заявки
        Registration.query.filter_by(event_id=event.id, status='pending').update(
            {'status': 'rejected'},
            synchronize_session=False
        )
        db.session.commit()
        flash('Квота волонтёров заполнена. Оставшиеся заявки отклонены.', 'info')
    
    flash('Заявка принята!', 'success')
    return redirect(url_for('main.event_detail', event_id=event.id))

@main_bp.route('/registration/<int:reg_id>/reject')
@login_required
def reject_registration(reg_id):
    reg = Registration.query.get_or_404(reg_id)
    if current_user.role.name not in ('admin', 'moderator'):
        abort(403)
    
    reg.status = 'rejected'
    db.session.commit()
    flash('Заявка отклонена', 'info')
    return redirect(url_for('main.event_detail', event_id=reg.event_id))




auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(login=form.login.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next') or url_for('main.index')
            flash('Вы успешно вошли в систему', 'success')
            return redirect(next_page)
        flash('Неверный логин или пароль', 'danger')
    return render_template('login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('main.index'))