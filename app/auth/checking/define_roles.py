from flask import redirect, url_for, flash, g, request
from flask_login import current_user
from functools import wraps
import webbrowser
from flask import render_template

def login_check(script=True):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.is_authenticated:
                return f(*args, **kwargs)
            else:
                if script:
                    #return redirect(url_for('login_bp.login'))
                    return "<script>$.ajax({url:'/auth/index',success: function(data) {$('body').empty().append(data)}})</script>"
                else:
                    return None
                #return redirect(url_for('login_bp.login'))
                #return '<script>window.location.href = "/auth/index"</script>'
                #return webbrowser.open('/'.join(request.url.split('/')[0:3]) + url_for('login_bp.login'))
        return decorated_function
    return decorator

def define_roles(*args, redir=False):
    roles = args
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if len([role for role in roles if role in current_user.get_roles()]) != 0:
                return f(*args, **kwargs)
            else:
                if redir:
                    flash('У Вас нет доступа к данному разделу')
                    return redirect(url_for('main_bp.get_main'))
        return decorated_function
    return decorator