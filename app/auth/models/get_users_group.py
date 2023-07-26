from app import db
from app.auth.models.users import User, Role

def get_user_group() -> dict:
    try:
        role_user = {}
        role = Role.query.all()
        role.sort(key=lambda x: x.name)
        for i, r in enumerate(role):
            role_user[i] = {'role_name': r.name, 'users': {u.name: u.active for г in r.us}}
        return {'error': False, 'data': role_user}
    except Exception as e:
        sys.tracebacklimit = 0
        return {'error': True, 'text_error': 'Ошибка: {}'.format(str(e))}

def change_users_group(user_id, role_id, add=False, remove=False):

    role = Role.query.filter_by(id=role_id).first()
    user = User.query.filter_by(id=user_id).first()
    relation = check_relation(role, user)

    db_func = None
    if remove and relation: db_func = role.us.remove 
    if add and not relation: db_func = role.us.append 
    
    if db_func:
        db_func(user)

    db.session.commit()


def delete_auth(id, type):

    models = {'role': Role, 'user': User}
    model = models[type]

    role = model.query.filter_by(id=id).delete()
    db.session.commit()


def check_relation(role, user):
    return user.id in [us.id for us in role.us]