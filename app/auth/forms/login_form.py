# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, PasswordField, BooleanField, SubmitField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Length, Regexp, EqualTo, DataRequired, Email
from app.auth.models.users import User

from app.settings import maketext


class LoginForm(FlaskForm):
    username = SelectField('Логин сотрудника:', coerce=str,
                        render_kw={'class': 'form-control form-username'},
                        default=''
                        )
    user_full_name = StringField('ФИО сотрудника',
                        render_kw={'class': 'form-control user-full-name', 'readonly': True},
                        default=''
                        )
    roles = SelectField('Роли сотрудника:', coerce=str,
                        render_kw={'class': 'form-control'},
                        choices = []
                        )

    password = PasswordField('Пароль:', validators=[DataRequired()],
                        render_kw={'class': 'form-control'}
                        )
    submit = SubmitField('Войти в систему',
                        render_kw={'class': 'form-control mt-4'}
                        )
