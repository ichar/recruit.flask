# -*- coding: utf-8 -*-

import os
from importlib import import_module

from flask import (
    Response, render_template, url_for, request, make_response, jsonify,
    g, current_app
    )
from flask_login import login_required, current_user

from config import (
    IsDebug, IsDeepDebug, IsTrace, IsPrintExceptions,
    basedir, errorlog, print_exception, print_to
    )

from ..settings import (
    DOCS_WITH_PDF, maketext, app_logger, product_version, 
    init_response, get_request_item
    )
from ..utils import Capitalize, getDate, getToday

from . import docs_bp

from .forms import (
    today, EventDate, check_request, 
    get_regions, get_persons, get_specialities, 
    makepdf
    )


##  =======================================
##  Модуль формирования выходных документов
##  =======================================


default_page = 'docs'
default_action = '200'
default_page_action = '201'
default_template = 'docs'
default_title = 'Application Output Form'

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


def get_selected_item(items, key):
    for i, k in enumerate(items):
        if k == key:
            return i
    return 0


def _check_extra_tabs(row):
    tabs = {}
    return tabs


def _valid_extra_action(action, row=None):
    return action


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
    page_title = maketext('%s %s' % (default_title, Capitalize(mode)))
    debug, kw = init_response(page_title, default_page)
    kw['product_version'] = product_version
    kw['mode'] = mode
    kw['with_starter'] = 1
    #
    # PDF mode:
    #   0 - don't use pdf
    #   1 - печать в тело ответа
    #   2 - печать в файл с текущим request_id:
    #       static/files/<request_id>-<mode>.pdf
    #
    kw['with_pdf'] = DOCS_WITH_PDF

    #   -----------------------
    #   Проверка метода запроса
    #   -----------------------

    if request.method == 'POST':
        is_refresh_mode_post = True
        is_refresh_mode_get = False
        default_submit_mode = 3
    else:
        is_refresh_mode_post = False
        is_refresh_mode_get = True
        default_submit_mode = 1

    kw['is_refresh_mode_post'] = is_refresh_mode_post and 1 or 0
    kw['default_submit_mode'] = default_submit_mode
    kw['page_starter'] = is_refresh_mode_post and 1 or 0

    template = ''

    #   --------------------
    #   Инициализация данных
    #   --------------------

    # [param:place] Место проведения мероприятия
    place = current_app.config['PLACE']

    args = check_request()

    # [param:period] Период проведения
    period = args.get('period')

    # [param:event] Наименование мероприятия
    event = 'Профессионально-психологичесий отбор'
    # [param:date_event] Дата мероприятия
    date_event = EventDate(getToday())

    # [param:expert] Специалист по профессиональному психологическому отбору
    expert = 'Специалист профессионального отбора %s' % current_user.short_name()

    # [param:persons] Список призывников
    persons = get_persons()

    # [param:specialities] Список ВУСов
    specialities = get_specialities()

    # [param:regions] Список регионов
    regions = get_regions()

    print_to(None, 'docs started... mode:[%s], default_submit_mode:[%s], args:%s' % ( 
            mode,
            default_submit_mode,
            args),
        request=request)

    #   --------------------
    #   Список типов отчетов
    #   --------------------

    reporttypes = (
        ('doc01', maketext('Output Form Doc01')),
        ('doc06', maketext('Output Form Doc06')),
        ('doc02', maketext('Output Form Doc02')),
        ('doc03', maketext('Output Form Doc03')),
        ('doc05', maketext('Output Form Doc05')),
        ('doc16', maketext('Output Form Doc16')),
        ('doc04', maketext('Output Form Doc04')),
        ('doc07', maketext('Output Form Doc07')),
        ('doc08', maketext('Output Form Doc08')),
        ('doc09', maketext('Output Form Doc09')),
        ('doc10', maketext('Output Form Doc10')),
        ('doc11', maketext('Output Form Doc11')),
        ('doc12', maketext('Output Form Doc12')),
        ('doc13', maketext('Output Form Doc13')),
        ('doc14', maketext('Output Form Doc14')),
        ('doc15', maketext('Output Form Doc15')),
    )

    #   ------------------------------------------------------------
    #   Контент в формате pdf:
    #
    #       with-pdf : int, флаг "использовать pdf"
    #       pdf_path : str, маршрут загрузки шаблона для формата pdf
    #   ------------------------------------------------------------

    with_pdf = kw.get('with_pdf')
    pdf_path = with_pdf and 'to_pdf/' or ''

    kw.update({
        'root'        : root,
        'basedir'     : basedir,
        'pagedir'     : pagedir,
        'title'       : page_title,
        'place'       : place,
        'loader'      : url_for('docs_bp.loader'),
        'empty_line'  : '',
        'reporttypes' : reporttypes,
        'report_date' : today(),
        'is_hidden'   : 1,
    })

    # Тип документа
    reporttype = args['reporttype']

    #   -----------------
    #   Генератор отчетов
    #   -----------------

    is_index = False

    if not mode or mode == 'index':
        template = 'docs/formation_docs%s.html'
        is_index = True

    elif mode.startswith('doc'):
        module = __import__('app.docs.forms.%s' % mode, fromlist=['render',])

        kw.update(module.render(mode, args=args, persons=persons, regions=regions, specialities=specialities))

    # Имя файла шаблона документа
    if not template:
        template = f'docs/{mode}%s.html'

    tree = regions.tree()

    # Атрибуты документа и формы генератора отчетов
    kw.update({
        'css'           : mode or None,
        'place'         : place,
        'event'         : event,
        'date_event'    : date_event,
        'expert'        : expert,
        'period'        : period,
        'persons'       : persons.items,
        'specialities'  : specialities.items,
        'regions'       : tree,
        'args'          : args,
        'print_mode'    : g.system_config.IsDocsPrintMode and mode.upper() or '',
    })

    if template:
        #
        # Два режима загрузки контента страницы: GET|POST
        #
        if with_pdf and not is_index:
            template_pdf = f'docs/{pdf_path}/{mode}_body.html'
            #
            #   Формирование отчета в формате pdf
            #
            body = render_template(template_pdf, **kw)
            pdf = makepdf(body, **kw)
            if pdf:
                response = Response(pdf, content_type='application/pdf')
                return response

        body = render_template(template % (is_refresh_mode_post and '_page' or ''), **kw)

        if is_refresh_mode_get:
            #
            # Метод GET: полное обновление контента страницы 
            # (default_submit_mode=1)
            # Строка запроса: URL страницы
            #
            return make_response(body)
        else:
            #
            # По умолчанию POST: обновление контента тега 'page_content' 
            # (default_submit_mode = 3)
            # AJAX-запрос
            #
            return body
    #
    # Иначе: контент(отчет) не определен (error)
    #
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

