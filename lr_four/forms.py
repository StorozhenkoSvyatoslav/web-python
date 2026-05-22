from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField
from wtforms.validators import DataRequired, ValidationError
import re

class UserForm(FlaskForm):
    login = StringField('Логин *', validators=[DataRequired(message='Поле "Логин" не может быть пустым!')])
    password = PasswordField('Пароль *', validators=[DataRequired(message='Поле "Пароль" не может быть пустым!')])
    first_name = StringField('Имя *', validators=[DataRequired(message='Поле "Имя" не может быть пустым!')])
    last_name = StringField('Фамилия *', validators=[DataRequired(message='Поле "Фамилия" не может быть пустым!')])
    middle_name = StringField('Отчество')
    role_id = SelectField('Роль', coerce=int)
    submit = SubmitField('Создать аккаунт')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from models import Role
        roles = Role.query.all()
        self.role_id.choices = [(0, "Без роли")] + [(r.id, f"{r.name} — {r.description}") for r in roles]
        
    def validate_login(self, field):
        login = field.data.strip()
        if len(login) < 5:
            raise ValidationError('Логин должен содержать не менее 5 символов!')
        elif not re.match(r'^[a-zA-Zа-яА-Яё0-9]+$', login):
            raise ValidationError('Логин должен содержать только латинские буквы и цифры!')
    
    def validate_password(self, field):
        password = field.data.strip()
        allowed_symbols = r'^[a-zA-Zа-яА-ЯёЁ0-9~!?@#$%^&*_\-+()\[\]{}></\\|\'".,;:]+$'
        if len(password) < 8:
            raise ValidationError('Пароль должен содержать не менее 8 символов!')
        elif len(password) > 128:
            raise ValidationError('Пароль должен содержать не более 128 символов!')
        elif ' ' in password:
            raise ValidationError('Пароль не должен содержать пробелов!')
        elif not re.search(r'[0-9]', password):
            raise ValidationError('Пароль должен содержать хотя бы одну цифру!')
        elif not re.match(allowed_symbols, password):
            raise ValidationError('Пароль содержит недопустимые символы!')
        elif not re.search(r'[A-ZА-Я]', password):
            raise ValidationError('Пароль должен содержать хотя бы одну заглавную букву!')
        elif not re.search(r'[a-zа-я]', password):
            raise ValidationError('Пароль должен содержать хотя бы одну строчную букву!')
        
