# -*- coding: utf-8 -*-

from functools import wraps
from flask import abort, request, redirect, render_template, current_app, make_response
from flask_login import current_user

from config import DEFAULT_ROOT

#
#   DON'T IMPORT utils HERE !!!
#

LIMITED_PAGES = ()

ROOT_URL = '/'

EXEMPT_METHODS = set(['OPTIONS'])


def forbidden(e):
    from .settings import make_platform
    kw = make_platform()
    kw.update({
        'root'       : ROOT_URL,
        'title'      : 'Forbidden Error Page',
        'module'     : 'auth',
        'width'      : 1080,
        'message'    : maketext('Access closed'),
        'pagination' : None,
    })
    return render_template('auth/403.html', **kw), 403


def is_limited(key):
    host = request.host
    public = DEFAULT_ROOT['public']
    return public and host in public and key in LIMITED_PAGES and True or False


def is_forbidden(key):
    """
    if current_user.is_superuser():
        return False
    if key == 'show' and not (current_user.app_is_office_direction):
        return True
    """
    return False

'''
def _login_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if request.method in EXEMPT_METHODS or current_app.config.get("LOGIN_DISABLED"):
            return func(*args, **kwargs)
        elif current_app.login_manager._login_disabled:
            return func(*args, **kwargs)
        elif not current_user.is_authenticated:
            return current_app.login_manager.unauthorized()
        elif request.path == '/auth/change_password':
            return func(*args, **kwargs)

        host = request.host
        link = request.path
        items = link.split('/')
        root = len(items) > 1 and items[1] or ROOT_URL
        public = DEFAULT_ROOT['public']

        base_url = ''
        app_menu = ''

        if is_limited(root):
            return redirect('/auth/default')
        elif is_forbidden(root):
            return redirect('/auth/forbidden')
        elif root == ROOT_URL and base_url and base_url != ROOT_URL:
            return redirect(base_url)
        return func(*args, **kwargs)

    return decorated_view

import flask_login

flask_login.login_required = _login_required
'''
