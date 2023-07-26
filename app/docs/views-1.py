# -*- coding: utf-8 -*-

import os
from importlib import import_module
from jinja2 import Environment, FileSystemLoader

from . import docs_bp

from ..settings import *

from .forms import *


##  ===================
##  Docs Viewer Package
##  ===================


default_page = 'docs'
default_action = '200'
default_page_action = '201'
default_template = 'docs'
default_title = 'Application Output Forms'


pagedir = os.path.abspath(os.path.dirname(__file__))

root = 'static'


def before(f):
    def wrapper(**kw):
        name = kw.get('engine') or 'default'
        #g.engine = DatabaseEngine(name=name, user=current_user, connection=CONNECTION[name])
        return f(**kw)
    return wrapper


@before
def refresh(**kw):
    g.requested_object = {}
    return


## ==================================================== ##


def _check_extra_tabs(row):
    tabs = {}
    return tabs


def _valid_extra_action(action, row=None):
    return action


def get_css(mode):
    css = '\n\n<style type="text/css">%s</style>'

    source = '/static/css/style.%s.css' % mode
    scr = os.path.join(basedir, source)

    with open(src, 'r', encoding=default_encoding) as fin:
        return css % fin.read()


def make_template(page_template, **kw):
    src = os.path.join(pagedir, 'templates/')
    env = Environment(loader=FileSystemLoader(src))
    template = env.get_template(page_template).render(**kw)

    mode = kw.get('mode')

    template += get_css('docs')
    if mode:
        template += get_css(mode)
    return template


@docs_bp.route('/', methods=['GET'])
@docs_bp.route('/index', methods=['GET', 'POST'])
@docs_bp.route('/<mode>', methods=['GET', 'POST'])
@docs_bp.route('/index/<mode>', methods=['GET', 'POST']) #, defaults={'mode': ''}
@login_required
#@define_roles('admin')
def start(mode=None):
    try:
        return index(mode or '')
    except Exception as err:
        if IsPrintExceptions:
            print_exception()
        raise


def index(mode):
    page_title = '%s %s' % (default_title, Capitalize(mode))
    debug, kw = init_response(page_title, default_page)
    kw['product_version'] = product_version
    kw['mode'] = mode
    kw['with_starter'] = 1

    print_to(None, f'docs started... mode:{mode}', request=request)

    template = ''

    #   ---------
    #   Data init
    #   ---------

    # [param:place] Место проведения мероприятия
    place = current_app.config['PLACE']

    args = check_request()
    
    # [param:period] Период проведения
    period = args.get('period')

    # [param:event] Наименование мероприятия
    event = 'Профессионально-психологичесий отбор'

    # [param:expert] Специалист по профессиональному психологическому отбору
    expert = 'Специалист профессионального отбора %s' % current_user.short_name()

    # [param:persons] Список призывников
    persons = get_persons()

    #   ------------
    #   Report types
    #   ------------

    reporttypes = (
        ('doc01', maketext('Output Form Doc01')),
        ('doc06', maketext('Output Form Doc06')),
        ('doc02', maketext('Output Form Doc02')),
        ('doc05', maketext('Output Form Doc05')),
        ('doc03', maketext('Output Form Doc03')),
        ('doc04', maketext('Output Form Doc04')),
    )

    kw.update({
        'root'        : root,
        'basedir'     : basedir,
        'pagedir'     : pagedir,
        'title'       : page_title,
        'loader'      : url_for('docs_bp.loader'),
        'empty_line'  : '',
        'reporttypes' : reporttypes,
        'report_date' : today(),
        'is_hidden'   : 1,
    })

    # Тип документа
    reporttype = args['reporttype']

    #   ----------------
    #   Report Generator
    #   ----------------

    if not mode or mode == 'index':
        template = 'docs/formation_docs%s.html'

    elif mode.startswith('doc'):
        module = __import__('app.docs.forms.%s' % mode, fromlist=['render',])

        kw.update(module.render(mode, args=args, persons=persons))

    # Атрибуты документа и формы генератора отчета
    kw.update({
        'css'        : mode or None,
        'place'      : place,
        'event'      : event,
        'expert'     : expert,
        'period'     : period,
        'persons'    : persons.items,
        'args'       : args,
    })

    if not template:
        template = f'docs/{mode}%s.html'

    #   ----------------------------
    #   Check type of request method
    #   ----------------------------

    if request.method == 'POST':
        is_refresh_mode_post = True
        is_refresh_mode_get = False
        default_submit_mode = 3;
    else:
        is_refresh_mode_post = False
        is_refresh_mode_get = True
        default_submit_mode = 1;

    kw['is_refresh_mode_post'] = is_refresh_mode_post and 1 or 0
    kw['default_submit_mode'] = default_submit_mode
    kw['page_starter'] = is_refresh_mode_post and 1 or 0

    if template:
        template_name = template % (is_refresh_mode_post and '_page' or '')
        template = make_template(template_name, **kw)

        if is_refresh_mode_get:
            return make_response(template.render(**kw))
        else:
            return template.render(**kw)

    return 'error: undefined template'


@docs_bp.route('/loader', methods = ['GET', 'POST'])
@login_required
def loader():
    try:
        return loader_start()
    except:
        if IsPrintExceptions:
            print_exception()

        app_logger('%s.loader' % default_page, maketext('Application error. See traceback.log for details'), is_error=True)

        raise


def loader_start():
    exchange_error = ''
    exchange_message = ''

    action = get_request_item('action') or default_action
    selected_menu_action = get_request_item('selected_menu_action') or action != default_action and action or default_page_action

    response = {}

    refer_id = get_request_item('refer_id') or '0'
    row_id = get_request_item('row_id') or '0'

    params = get_request_item('params') or None

    refresh(refer_id=refer_id)

    if IsDeepDebug:
        print('--> action:%s refer_id:%s params:%s' % (action, refer_id, params))

    if IsTrace:
        print_to(errorlog, '--> loader:%s %s [%s:%s]%s' % (
                 action,
                 current_user.name,
                 refer_id,
                 selected_menu_action,
                 params and ' params:[%s]' % params or '',
            ))

    currentfile = None
    sublines = []
    config = None

    data = {}
    number = ''
    columns = []
    total = 0
    status = ''
    path = None

    props = None
    errors = None

    tabs = _check_extra_tabs(g.requested_object)

    try:
        if action == default_action:
            #
            #   Default page action
            #
            action = _valid_extra_action(selected_menu_action) or default_page_action

        elif action == default_page_action:
            pass

        if not action:
            pass

        if action in ('100','101'):
            #
            #   Load Page Static (css | js)
            #
            data = {}
            mode = params.get('mode')
            css_files = []
            if not mode or mode.startswith('doc'):
                css_files = ['docs', 'skins.web']
            if mode not in css_files:
                css_files.append(mode)
            data['statics'] = [f'<link ext="1" rel="stylesheet" href="docs/static/css/style.{css}.css">'
                               for css in css_files]

        if action in ('100','102'):
            pass

    except:
        print_exception()

    response.update({
        'action'           : action,
        # --------------
        # Service Errors
        # --------------
        'exchange_error'   : exchange_error,
        'exchange_message' : exchange_message,
        # -----------------------------
        # Results (Log page parameters)
        # -----------------------------
        'refer_id'         : refer_id,
        # ----------------------------------------------
        # Default Lines List (sublines equal as batches)
        # ----------------------------------------------
        'currentfile'      : currentfile,
        'sublines'         : sublines,
        'config'           : config,
        'tabs'             : list(tabs.keys()),
        # --------------------------
        # Results (Log page content)
        # --------------------------
        'total'            : total or len(data),
        'data'             : data,
        'status'           : status,
        'path'             : path,
        'props'            : props,
        'columns'          : columns,
        'errors'           : errors,
    })

    return jsonify(response)

