import re
from flask import jsonify

from app.auth.models.users import User, Role

def password_validate(password):
    pattern_password = re.compile(r'^(?=.*[0-9].*)(?=.*[a-z].*)(?=.*[A-Z].*)')
    return bool(pattern_password.match(password)) and len(password) > 5

def auth_mistake_catch(form_dict, model, user=None):

    user_exist = model.query.filter(model.name==form_dict['name'], model.id!=form_dict.get('id')).first()    

    if 'id' in form_dict and 'current_password' in form_dict:
        if not User.check_password(user.first(), form_dict['current_password']):
            return jsonify({'error': True,
                'banner': 'Ошибка заполнения',
                'error_human_text': 'Неверно введен текущий пароль',
                'error_text': ''})

    if 'password_hash' in form_dict:
        if form_dict['password_hash'] != form_dict['password_again']:
            return jsonify({'error': True,
                'banner': 'Ошибка заполнения',
                'error_human_text': 'Введенные пароли не совпадают',
                'error_text': ''})
        
    if user_exist:
        auth_type = 'Пользователь с таким логином' if model == User else 'Группа пользователей с таким названием'
        model_type = 'пользователя' if model == User else 'группы пользователей'

        return jsonify({'error': True,
                'banner': 'Ошибка создания ' + model_type,
                'error_human_text': auth_type + ' уже существует',
                'error_text': ''})

    if 'password_hash' in form_dict:
        if form_dict['password_hash'] != '' and not password_validate(form_dict['password_hash']):       
            return jsonify({'error': True,
                'banner': 'Ошибка пользователя',
                'error_human_text': 'Пароль должен состоять не менее чем из 6 символов, в него должны быть включены цифры, а также латинские буквы верхнего и нижнего регистров',
                'error_text': ''})

    return False