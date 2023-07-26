# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-

import os
import sys
import re
import random
import decimal
import json
from datetime import datetime
import pytz
import logging

# https://pypi.org/project/user-agents/
# from user_agents import parse as user_agent_parse

from ua_parser import user_agent_parser
from werkzeug.user_agent import UserAgent
from werkzeug.utils import cached_property

#from flask import Response, abort, render_template, url_for, redirect, request, make_response, jsonify, flash, stream_with_context
#from flask_login import login_required
#from werkzeug.utils import secure_filename

from flask import request, flash, g, session, current_app
from flask_login import current_user
from flask import json

from config import (
     IsDebug, IsDeepDebug, IsTrace, IsLogTrace, IsShowLoader, IsForceRefresh, IsPrintExceptions, IsDisableOutput, IsFlushOutput,
     errorlog, print_to, print_exception, default_system_locale, 
     UTC_FULL_TIMESTAMP, TIMEZONE
)

from .utils import make_config, isIterable
from .messages import MESSAGES


##  ==========================
##  Общие настройки приложения
##  ==========================


def setup_locale():
    """
        Устанавливает языковой стандарт системы специально для Astra Linux.
        Примечание! Проблемы с декодированием | кодированием из объектов файловой системы    
    """
    import os
    import locale
    import platform

    if locale.getlocale()[0] is None:
        locale.setlocale(locale.LC_ALL, default_system_locale)
    info = {'loc': locale.getlocale(), 'lod_def': locale.getdefaultlocale()}

    if IsDeepDebug and IsLogTrace:
        print_to(None, '>>> locale: %s os:%s platform:%s' % (info,  os.name, platform.system()))


def maketext(key, lang=None, force=None):
    """
        Переводит текст с en на ru.
        Словарь используемых сообщений. Вместо babel
    """
    text = '' #gettext(key)
    if not text or text == key or force:
        if key in MESSAGES:
            text = MESSAGES[key][lang or DEFAULT_LANGUAGE]
    return text or key


#
#   DON'T IMPORT utils HERE !!!
#

product_version = ('0.1', 'Beta, 2023-05-25')

#########################################################################################

#   ---------------------
#   Package Default types
#   ---------------------

DEFAULT_LANGUAGE = 'ru'

#   ---------------------------------------------------------------
#   Маркер по умолчанию для вывода документов [DEFAULT_DOCS_MARKER]
#   ---------------------------------------------------------------

DEFAULT_DOCS_MARKER = u'\u2713'
DEFAULT_DOCS_MINUS = u'\u2013'

DEFAULT_UNDEFINED = '---'
DEFAULT_DATE_FORMAT = ('%d/%m/%Y', '%d-%m-%Y',)
DEFAULT_DATETIME_FORMAT = '<nobr>%Y-%m-%d</nobr><br><nobr>%H:%M:%S</nobr>'
DEFAULT_HTML_SPLITTER = '_'

#   ------------------------------------------------------------------------------------------------
#
#   Режим ответа [DEFAULT_SUBMIT_MODE]:
#       0 -- db.controller.$onParentFormSubmit
#       1 -- db.controller.$onPageLinkSubmit (то же, что и изменение местоположения = app.menu._dialog_submit)
#       2 -- db.controller.$Handle(default_action, default_handler, default_params)
#       3 -- app.menu._dialog_start#
#
#   ------------------------------------------------------------------------------------------------

DEFAULT_SUBMIT_MODE = 1

DOCS_WITH_PDF = 0

EMPTY_VALUE = '...'

MAX_TITLE_WORD_LEN = 50

default_locale= 'rus' # synonym of system locale

# action types
VALID_ACTION_TYPES = ('100', '101', '102', '200', '201',)

APP_MODULES = (
    'docs',
)

APP_MENUS = [
    'default',
]

## ================================================== ##


class DataEncoder(json.JSONEncoder):
    """
        Кодировщик данных Json в ответ на некоторые типы данных (decimal...)
    """
    def default(self, ob):
        if isinstance(ob, decimal.Decimal):
            return str(ob)
        return json.JSONEncoder.default(self, ob)


class ParsedUserAgent(UserAgent):
    """
        Парсер пользовательского агента:
             ОС (family)
             браузер
    """
    @cached_property
    def _details(self):
        return user_agent_parser.Parse(self.string)

    @property
    def os(self):
        return self._details['os']

    @property
    def platform(self):
        return self.os['family']

    @property
    def browser(self):
        return self._details['user_agent']['family']

    @property
    def version(self):
        s = ''
        for key in ('major', 'minor', 'patch'):
            part = self._details['user_agent'][key]
            if (part) is not None:
                s += part
        return s


def app_logger(mode, message, force=None, is_error=False, is_warning=False, is_info=False, data=None, **kw):
    """
         Функция для создания файла ежедневного журнала logs/*.log
         Используется в flask proxy: g.app_logger
        
         Аргументы:
             режим -- название модели (такое же, как название модели или расширение)
             сообщение -- текст сообщения
        
         Аргументы ключевого слова (необязательно):
             force -- флаг принудительного запуска
             Уровни диагностики:
                 is_error -- ошибка
                 is_warning -- предупреждение
                 is_info -- информация
    
         Пример кода:
             debug, kw = init_response(page_title, default_page)
             |
             V
             app_logger(mode, '%s "%s"' % (maketext('Module start'), _title), is_info=True, host=host)
        
         Пример вывода:
                 2023-05-21 17:48:54 : app.settings-INFO >>> : режим [auth] : 127.0.0.1 : http://localhost:5000/ : login=[admin] : Вход в приложение
        
         Может дублироваться в системном файле traceback.log (IsDeepDebug=1).
        
         Для отклонения: IsLogTrace= 0, IsDeepDebug=0    
    """
    if IsDisableOutput:
        return
    line = ': mode[{mode}] : {ip} : {host} : login=[{login}] : {message} {data}'.format(
        mode=mode,
        ip=request.remote_addr,
        host=kw.get('host') or request.form.get('host') or request.host_url,
        login=current_user.is_authenticated and current_user.name or 'AnonymousUser',
        message=message,
        data=data and '\n%s' % data or '',
    )
    if IsDeepDebug:
        print_to(None, line)
    if IsLogTrace and g.app_logging is not None:
        if is_error:
            g.app_logging.error(line)
        elif is_warning:
            g.app_logging.warning(line)
        elif IsTrace and (force or is_info):
            g.app_logging.info(line)
    if IsFlushOutput:
        sys.stdout.flush()


def setup_logging(log):
    """
        Настройка файла ежедневного журнала (используемое ведение журнала)
    """
    try:
        if g.app_logger is not None:
            return
    except:
        pass

    P_TIMEZONE = pytz.timezone(TIMEZONE)

    logging.basicConfig(
        filename=log,
        format='%(asctime)s : %(name)s-%(levelname)s >>> %(message)s', 
        level=logging.DEBUG, 
        datefmt=UTC_FULL_TIMESTAMP,
    )

    g.app_logging = logging.getLogger(__name__)
    g.app_logger = app_logger


def clearFlash(msg, is_save_one=None):
    """
        Очищает список сообщений flash werkzeug и отправляет только одно указанное внутри
    """
    key = '_flashes'
    if key not in session:
        return
    is_exist = 0
    for i, (m, x) in enumerate(session[key]):
        if msg == x:
            is_exist = 1
        if not x:
            pass
    if is_exist:
        session['_flashes'].clear()
    if is_save_one:
        flash(msg)

## -------------------------------------------------- ##

_agent = None
_user_agent = None

#
#   Управление типами браузеров
#

def IsAndroid():
    return _agent.platform == 'android'
def IsiOS():
    return _agent.platform == 'ios' or 'iOS' in _user_agent.platform
def IsiPad():
    return _agent.platform == 'ipad' or 'iPad' in _user_agent.platform
def IsLinux():
    return _agent.platform == 'linux'
def IsAstra():
    return _agent.platform == 'linux' and _agent.browser == 'firefox'

def IsChrome():
    return _agent.browser == 'chrome'
def IsFirefox():
    return _agent.browser == 'firefox'
def IsSafari():
    return _agent.browser == 'safari' or 'Safari' in _user_agent.browser
def IsOpera():
    return _agent.browser == 'opera' or 'Opera' in _user_agent.browser

def IsIE(version=None):
    ie = _agent.browser.lower() in ('explorer', 'msie',)
    if not ie:
        return False
    elif version:
        return float(_agent.version) == version
    return float(_agent.version) < 10
def IsSeaMonkey():
    return _agent.browser.lower() == 'seamonkey'
def IsEdge():
    return 'Edge' in _agent.string
def IsMSIE():
    return _agent.browser.lower() in ('explorer', 'ie', 'msie', 'seamonkey',) or IsEdge()

def IsMobile():
    return IsAndroid() or IsiOS() or IsiPad()
def IsNotBootStrap():
    return IsIE(10) or IsAndroid()
def IsWebKit():
    return IsChrome() or IsFirefox() or IsOpera() or IsSafari()

def BrowserVersion():
    return _agent.version

def BrowserInfo(force=None):
    mobile = 'IsMobile:[%s]' % (IsMobile() and '1' or '0')
    info = 'Browser:[%s] %s Agent:[%s]' % (_agent.browser, mobile, _agent.string)
    browser = IsMSIE() and 'IE' or IsOpera() and 'Opera' or IsChrome() and 'Chrome' or IsFirefox() and 'FireFox' or IsSafari() and 'Safari' or None
    if force:
        return info
    return browser and '%s:%s' % (browser, mobile) or info


#   --------------------------------------------------------------
#   Вспомогательные функции для работы с запросом (объект request)
#   --------------------------------------------------------------

def get_request_item(name, check_int=None, args=None, is_iterable=None, **kw):
    """
        Возвращает значение элемента запроса по заданному имени параметра
        
        Arguments:
            name -- (str), имя параметра
        
        Keyword arguments (optional):
            check_int -- (bool), значение может быть просто int
            args=None -- (ob) объект аргументов GET-запроса, по некоторым причинам
            is_iterable -- (bool) перевести на итерируемый (список)    
    """
    x = None
    delimeter = kw.get('delimeter')
    splitter = kw.get('splitter')
    if args:
        x = args.get(name)
    elif request.method.upper() == 'POST': 
        if is_iterable and not delimeter:
            x = request.form.getlist(name)
        else:
            x = request.form.get(name)
    else:
        x = request.args.get(name)
    if x and is_iterable:
        if isIterable(x):
            return x
        if delimeter:
            value = x
            values = x.split(delimeter)
            if splitter and splitter in x:
                values = [x.replace(splitter, '') for x in values]
            return values

    if not x and (not check_int or (check_int and x in (None, ''))):
        x = request.args.get(name)
    if check_int:
        if x in (None, ''):
            return None
        elif x.isdigit():
            return int(x)
        elif ':' in x:
            return x
        elif x in 'yY':
            return 1
        elif x in 'nN':
            return 0
        else:
            return None
    if x and isinstance(x, str):
        if x == DEFAULT_UNDEFINED or x.upper() == 'NONE':
            x = None
        elif x.startswith('{') and x.endswith('}'):
            return eval(re.sub('null', '""', x))
    return x or ''


def get_request_items():
    """
        Возвращает все параметры: form (POST) или args (GET)
    """
    return request.method.upper() == 'POST' and request.form or request.args


def has_request_item(name):
    """
        Проверяет, присутствует ли данный параметр в запросе
    """
    return name in request.form or name in request.args


def get_request_search():
    """
        Проверяет только параметр «search»
    """
    return get_request_item('reset_search') != '1' and get_request_item('search') or ''


def get_user_agent():
    """
        Возвращает параметры пользовательского агента
    """
    return ParsedUserAgent(request.headers.get('User-Agent')) # request.user_agent


def make_platform(mode=None, debug=None):
    """
        Опрашивает платформу (формирует параметры браузера пользователя внутри объекта ответа)
    """
    global _agent, _user_agent

    agent = get_user_agent()
    browser = agent.browser

    if browser is None:
        return { 'error' : 'Access is not allowed!' }

    os = agent.platform
    root = '%s/' % request.script_root

    _agent = agent
    _user_agent = agent

    is_astra = ('%s' % (_user_agent)) == 'PC / Linux / Firefox 90.0' and 1 or 0

    if IsTrace and g.system_config.IsLogAgent:
        print_to(errorlog, 'user_agent:[%s]' % _user_agent)
        print_to(errorlog, '\n==> os:[%s], astra[%s], agent:%s[%s], browser:%s' % (os, is_astra, repr(agent), _user_agent, browser), request=request)

    try:
        is_superuser = current_user.is_superuser(private=True)
        is_owner = 0
        is_admin = current_user.is_administrator(private=False)
        is_manager = current_user.is_manager(private=True)
        is_operator = current_user.is_operator(private=True)
    except:
        pass

    sidebar_state = 0

    referer = ''
    links = {}

    is_mobile = IsMobile()
    is_default = 1 or os in ('ipad', 'android',) and browser in ('safari', 'chrome',) and 1 or 0 
    is_frame = not is_mobile and 1 or 0

    version = agent.version
    css = IsMSIE() and 'ie' or is_mobile and 'mobile' or 'web'

    platform = '[os:%s, browser:%s (%s), css:%s, %s %s%s%s]' % (
        os, 
        browser, 
        version, 
        css, 
        default_locale, 
        is_default and ' default' or ' flex',
        is_frame and ' frame' or '', 
        debug and ' debug' or '',
    )

    kw = {
        'os'             : os, 
        'platform'       : platform,
        'root'           : root, 
        'back'           : '',
        'agent'          : agent.string,
        'version'        : version, 
        'browser'        : browser, 
        'browser_info'   : BrowserInfo(0),
        'is_linux'       : IsLinux() and 1 or 0,
        'is_astra'       : is_astra and 1 or 0,
        'is_demo'        : 0, 
        'is_frame'       : is_frame, 
        'is_mobile'      : is_mobile and 1 or 0,
        'is_superuser'   : is_superuser and 1 or 0,
        'is_admin'       : is_admin and 1 or 0,
        'is_operator'    : (is_operator or is_manager or is_admin) and not is_owner and 1 or 0,
        'is_show_loader' : IsShowLoader,
        'is_explorer'    : IsMSIE() and 1 or 0,
        'is_hidden'      : 0,
        'css'            : css, 
        'referer'        : referer, 
        'bootstrap'      : '',
        'model'          : 0,
    }

    if mode:
        kw[mode] = True

    kw['bootstrap'] = ''

    kw.update({
        'with_starter'   : 1,
        'links'          : links, 
        'screen'         : request.form.get('screen') or '',
        'scale'          : request.form.get('scale') or '',
        'usertype'       : is_manager and 'manager' or is_operator and 'operator' or 'default',
        'sidebar'        : {'state' : sidebar_state, 'title' : maketext('Click to close top menu')},
        'avatar'         : '',
        'with_avatar'    : 0,
        'with_post'      : 1,
        'logo'           : '', 
        'image_loader'   : '%s%s' % (root, 'static/img/loader.gif'), 
    })

    kw['default_submit_mode'] = g.system_config.DefaultSubmitMode or DEFAULT_SUBMIT_MODE
    kw['is_active_scroller'] = 0

    kw['vsc'] = vsc(force=g.system_config.IsForceRefresh)

    if IsTrace and IsDeepDebug:
        print_to(errorlog, '--> make_platform:%s' % mode)

    return kw


def make_keywords():
    """
        Возвращает переведенные сообщения, особенно для внешнего javascript
    """
    return (
    # --------------
    # Error Messages
    # --------------
    "'Execution error':'%s'" % maketext('Execution error'),
    # -------
    # Buttons
    # -------
    "'OK':'%s'" % maketext('OK', force=1),
    "'Cancel':'%s'" % maketext('Cancel', force=1),
    "'Confirm':'%s'" % maketext('Confirm', force=1),
    # ----
    # Help
    # ----
    "'Attention':'%s'" % maketext('Attention'),
    # --------------------
    # Flags & Simple Items
    # --------------------
    "'error':'%s'" % maketext('error'),
    "'true':'%s'" % 'true',
    "'false':'%s'" % 'false',
    # ------------------------
    # Miscellaneous Dictionary
    # ------------------------
    "'batch':'%s'" % maketext('batch'),
    # ------------------------
    # Errors and Notifications
    # ------------------------
    "'Should be present date from-to value':'%s'" % maketext('Should be present date from-to value'),
    "'Should be present person value':'%s'" % maketext('Should be present person value'),
    "'Should be present speciality value':'%s'" % maketext('Should be present speciality value'),
    "'Should be present region value':'%s'" % maketext('Should be present region value'),
    )


def init_response(title, mode):
    """
        Инициализирует объект ответа
    """
    host = request.form.get('host') or request.host_url

    _title = '%s. %s' % (maketext('AppName'), title)

    app_logger(mode, '%s "%s"' % (maketext('Module start'), _title), is_info=True, host=host)

    if 'debug' in request.args:
        debug = request.args['debug'] == '1' and True or False
    else:
        debug = None

    kw = make_platform(mode, debug=debug)
    keywords = make_keywords()
    forms = ('index', 'admin', 'main', 'docs')

    now = datetime.today().strftime(DEFAULT_DATE_FORMAT[1])

    kw.update({
        'title'        : _title,
        'host'         : host,
        'locale'       : default_locale, 
        'language'     : 'ru',
        'keywords'     : keywords, 
        'forms'        : forms,
        'now'          : now,
        'action_id'    : get_request_item('action_id') or '0',
        'page_starter' : 0,
    })

    kw['selected_data_menu_id'] = get_request_item('selected_data_menu_id')
    kw['window_scroll'] = get_request_item('window_scroll')
    kw['avatar_width'] = '80'

    return debug, kw


def vsc(force=False):
    """
        Генерирует специальный аргумент внутри LINK-тегов для принудительной загрузки статических файловых объектов
    """
    return (IsIE() or IsForceRefresh or force) and ('?%s' % str(int(random.random()*10**12))) or ''


## ==================================================== ##


def load_system_config(user=None):
    """
        Загружает system_config.attrs для элементов динамической конфигурации.
        Используется внутри flask g-proxy
        
        Выполнение:
            g.system_config[<параметр>]        
    """
    g.system_config = make_config('system_config.attrs')
