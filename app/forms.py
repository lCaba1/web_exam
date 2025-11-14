from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DateField, TextAreaField, FileField, SubmitField
from wtforms.validators import DataRequired, NumberRange
from flask_wtf.file import FileAllowed, FileRequired
from wtforms import PasswordField, BooleanField

class LoginForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')

class EventForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    description = TextAreaField('Описание (Markdown)')
    date = DateField('Дата', format='%Y-%m-%d', validators=[DataRequired()])
    place = StringField('Место', validators=[DataRequired()])
    volunteers_required = IntegerField('Требуемое количество волонтёров', validators=[DataRequired(), NumberRange(min=1)])
    image = FileField('Изображение мероприятия', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Только изображения!')])
    submit = SubmitField('Сохранить')