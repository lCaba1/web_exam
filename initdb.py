from app import create_app, db
from app.models import User, Role
from werkzeug.security import generate_password_hash
from sqlalchemy import text

app = create_app()

with app.app_context():
    db.session.rollback()
    with db.engine.connect() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS=0;"))
        conn.commit()
    db.drop_all()
    with db.engine.connect() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS=1;"))
        conn.commit()
    db.create_all()
    admin_role = Role(name='admin', description='Administrator')
    moder_role = Role(name='moderator', description='Moderator')
    user_role = Role(name='user', description='Regular user')
    db.session.add_all([admin_role, moder_role, user_role])
    db.session.commit()
    users = [
        User(
            login='admin',
            password_hash=generate_password_hash('admin'),
            first_name='Админ',
            last_name='Админов',
            middle_name='',
            role=admin_role
        ),
        User(
            login='moderator',
            password_hash=generate_password_hash('moderator'),
            first_name='Мод',
            last_name='Ератор',
            middle_name='',
            role=moder_role
        ),
        User(
            login='user1',
            password_hash=generate_password_hash('user1'),
            first_name='Пользователь',
            last_name='Один',
            middle_name='',
            role=user_role
        ),
        User(
            login='user2',
            password_hash=generate_password_hash('user2'),
            first_name='Пользователь',
            last_name='Два',
            middle_name='',
            role=user_role
        ),
        User(
            login='user3',
            password_hash=generate_password_hash('user3'),
            first_name='Пользователь',
            last_name='Три',
            middle_name='',
            role=user_role
        )
    ]
    db.session.add_all(users)
    db.session.commit()
