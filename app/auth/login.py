# -*- coding: utf-8 -*-

import os

#from datetime import timedelta
#from werkzeug.urls import url_quote, url_unquote
#from flask import session, jsonify

from config import (
    IsDebug, IsDeepDebug, IsTrace, IsPrintExceptions, IsPageClosed,
    basedir, errorlog, print_exception, print_to, page_redirect,
    LOCAL_EASY_DATESTAMP, LOG_PATH, LOG_NAME
    )

from flask import Response, abort, render_template, url_for, redirect, request, jsonify, flash, g
from flask import session, current_app
from werkzeug.datastructures import MultiDict
from flask_login import login_user, logout_user, login_required, current_user

from .forms.login_form import LoginForm
from .models.users import User

from ..settings import (
    setup_locale, maketext, load_system_config, setup_logging, get_request_item, make_platform,
    app_logger
    )
from ..utils import normpath, getDate, getToday

from . import login_bp


IsResponseNoCached = 0

_EMERGENCY_EMAILS = ('odm@dipcenter.ru',)
_LOGIN_MESSAGE = 'Please log in to access this page.'
_MIN_REGISTERED_USER = 1
_MODULE = 'auth'


##  ==================================
##  Модуль аутентификации пользователя
##  ==================================


def _init():
    setup_locale()
    g.current_user = current_user
    g.maketext = maketext
    g.app_product_name = maketext('AppProductName')

    load_system_config(current_user)

    today = getDate(getToday(), format=LOCAL_EASY_DATESTAMP)
    log = normpath(os.path.join(basedir, LOG_PATH, '%s_%s.log' % (today, LOG_NAME)))

    g.users_registered_required = False

    setup_logging(log)


@login_bp.before_app_request
def before_request():

    if IsDeepDebug:
        if not current_user.is_anonymous:
            print('--> before_request:is_authenticated:%s path:[%s]' % (
                current_user.is_authenticated, request.path))

    if not request.endpoint:
        pass #return redirect(url_for('login_bp.login')) # XXX
    elif 'static' in request.endpoint:
        pass
    elif request.endpoint[:5] == 'auth.' or not current_user.is_authenticated:
        pass
    else:
        if IsTrace and IsDeepDebug:
            print_to(errorlog, '--> before_request endpoint:%s, current_user:%s path:[%s]' % (
                request.endpoint, current_user, request.path))

        _init()


## ============================ ##


def get_users():
    users = [(item.name, item.name) for item in User.query.all()]
    users.insert(0, ('', maketext('Check login')))
    return users


def getUserForm(is_form_only=None):
    form = LoginForm(formdata=MultiDict())
    place = current_app.config['PLACE']
    users = get_users()
    form.username.choices = users
    form.username.default = 0
    if is_form_only:
        return form, place
    return form, users, place


@login_bp.route('/user_info', methods=['POST'])
def user_info():
    try:
        selected = get_request_item('selected')
        form, users, place = getUserForm()
        if selected:
            user = User.get_by_name(selected)

            roles = [(r.name, r.name) for r in user.roles]

            form.user_full_name.default = user.full_name
            form.username.default = selected
            form.roles.choices = roles
            form.process()

        renderer = render_template('auth/form.html', form=form)
        return jsonify({'form': renderer})

    except:
        if IsPrintExceptions:
            print_exception()


@login_bp.route('/default', methods=['GET', 'POST'])
@login_required
def default(link=None):
    return redirect(link or url_for('main_bp.get_main'))


@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
        Главный обработчик авторизации
        Запрос может состоять из attr `next`, следующего за URL-адресом маршрута.    
    """
    title = 'Application Login'

    def _get_current_url():
        next = request.args.get('next')
        return next not in ('', '/') and next

    accessed_link = _get_current_url()

    form, place = getUserForm(is_form_only=1)

    user = None
    kw = {}

    try:
        if not current_user.is_authenticated:
            username = request.form.get('username')
            password = request.form.get('password')

            if form is not None and username: # and form.validate_on_submit():
                user = User.get_by_name(username)

                if not user or not user.check_password(password):
                    flash(maketext('Invalid username or password.'))
                    return redirect(url_for('login_bp.login'))

                login_user(user, remember=True)
                #session['test_cancel'] = True

        if current_user.is_authenticated:
            if IsTrace:
                print_to(errorlog, '\n==> login:%s remote_addr:%s active:%s' % (
                    current_user.name, request.remote_addr, current_user.is_active),
                    request=request)

            _init()

            g.current_user_login = current_user.name

            kw = make_platform(mode='auth')

            app_logger(_MODULE, title, is_info=True)

            return default(accessed_link)

    except:
        if IsPrintExceptions:
            print_exception()

    return render_template('auth/login.html', form=form, **kw)


@login_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('username', None)
    logout_user()
    return redirect(url_for('login_bp.login'))


@login_bp.route('/forbidden')
def forbidden():
    abort(403)
