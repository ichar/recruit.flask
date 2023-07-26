
from flask import render_template, redirect, url_for, session, current_app
from flask_login import logout_user, login_required, current_user, login_required

from app.main import main_bp

from app.models.themes import params_css

from ..settings import *
from ..utils import Capitalize


default_page = 'main'
default_template = 'main'
default_title = 'Application Main'

##  ========================
##  Main Application Package
##  ========================


def roles_accepted(*args):
    for role in args:
        if current_user.has_role(role):
            return True
    return False


@main_bp.route('/', methods=['GET', 'POST'])
@main_bp.route('/index', methods=['GET', 'POST'])
@main_bp.route('/main', methods=['GET', 'POST'])
@login_required
def get_main():
    '''
    session.pop('_flashes', None)
    if 'next' in session:
        session.pop('next')
    '''
    mode = 'recruit'
    page_title = '%s %s' % (default_title, Capitalize(mode))
    debug, kw = init_response(page_title, default_page)

    place = current_app.config['PLACE']
    user = current_user.get_fio()
    permit_view = roles_accepted('admin', 'manager', 'security', 'operator', 'spec_ppo')

    kw.update({
        'title'       :'Призывник ВС', 
        'params_css'  : params_css(), 
        'place'       : place, 
        'user'        : user,
        'permit_view' : permit_view,
        'loader'      : '',
    })
    
    if permit_view:
        return render_template('%s/main.html' % default_template, **kw)


'''
@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login_bp.login'))
'''




