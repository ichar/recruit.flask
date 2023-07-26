import uuid

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SelectMultipleField
from wtforms.fields import DateField
from wtforms.validators import DataRequired, EqualTo

from app.models.unified_documents import Official, OfficialsRole
from app.auth.models.users import Role, User



def add_string_field(form, id, label, input_class, value, update=0, data=False):

    setattr(form,
            id,
            StringField(label,
                        render_kw={'class': 'form-control ' + input_class,
                                    'value': value,
                                    'data': data,
                                    'update': update,
                                    },        
            ))
    
def add_password_field(form, id, label, input_class):

    setattr(form,
            id,
            PasswordField(label,
                        render_kw={'class': 'form-control ' + input_class,
                                    },        
            ))
    
def add_selected_field(form, id, label, choices, disabled=False):

    setattr(form, 
            id,
            SelectField(label,
                        option_widget=True,
                        choices = choices,

                        render_kw={'class': 'form-control input_auth',
                                   'disabled': disabled,
                                   }))
    
def add_multy_selected_field(form, id, label, choices):

     setattr(form, 
            id,
            SelectMultipleField(label,
                        option_widget=True,
                        choices = choices,
                        render_kw={'class': 'form-control input_auth',
                                   }))


def generate_user_form(edit_user=False):

    class F(FlaskForm):
            pass
    
    if edit_user:
        user = User.query.filter(User.id==edit_user).first()
        name= user.name
        user_name= user.user_name
        user_surname = user.user_surname
        user_patronymic = user.user_patronymic
        update = 1
        requared_input = ''
        pasword_label = 'Новый пароль'

    else:
        name, user_name, user_surname, user_patronymic, update, requared_input, pasword_label = '', '', '', '', 0, 'requared_input', 'Пароль'

        choices = [(role.id, role.name) for role in OfficialsRole.query.all()]
        choices.insert(0, ('empty', '-- Выберете должность --'))

        add_selected_field(F, 'oficials_roles', 'Должность', choices)
        add_selected_field(F, 'official', 'Должностное лицо', ['-- Выберете должностное лицо --'], disabled=True)

    add_string_field(F, 'name', 'Логин', 'requared_input', name, update=update, data=edit_user)
    add_string_field(F, 'user_name', 'Имя', 'requared_input', user_name)
    add_string_field(F, 'user_surname', 'Фамилия', 'requared_input', user_surname)
    add_string_field(F, 'user_patronymic', 'Отчество', 'requared_input', user_patronymic)

    if edit_user:
        add_password_field(F, 'current_password', 'Действующий пароль', 'requared_input')
    else:
         choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
         add_multy_selected_field(F, 'roles', 'Пользовательские группы', choices)

    add_password_field(F, 'password_hash', pasword_label, requared_input)
    add_password_field(F, 'password_again', 'Повторите пароль', requared_input)

    F().process()
    return F()

def generate_roles_form(edit_user=None):

    class F(FlaskForm):
            pass
    
    if edit_user:
        data = edit_user
        role = Role.query.filter(Role.id==edit_user).first()
        name = role.name
        description = role.description
        update = 1

    else:
        name, description, update, data = '', '', 0, False

    add_string_field(F, 'name', 'Название', 'requared_input', name, update=update, data=data)
    add_string_field(F, 'description', 'Описание', 'requared_input', description)

    F().process()
    return F()
