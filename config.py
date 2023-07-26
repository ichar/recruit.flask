# -*- coding: utf-8 -*-

import os
import sys
import codecs
import datetime
import traceback
import re

from dotenv import load_dotenv
from collections import Iterable

basedir = os.path.abspath(os.path.dirname(__file__))
errorlog = os.path.join(basedir, 'traceback.log')

dotflaskenv_path = os.path.join(basedir, '.flaskenv')
dotenv_path = os.path.join(basedir, '.env')

load_dotenv(dotenv_path)
load_dotenv(dotflaskenv_path)

# ----------------------------
# Global application constants
# ----------------------------

IsDebug                = 1  # sa[stdout]: prints general info (1 - forbidden with apache!)
IsDeepDebug            = 0  # sa[stdout]: prints detailed info (1 - forbidden with apache!)
IsTrace                = 1  # Trace[errorlog]: output execution trace for http-requests
IsPrintExceptions      = 1  # Flag: sets printing of exceptions
IsForceRefresh         = 1  # Flag: sets http forced refresh for static files (css/js)
IsDisableOutput        = 0  # Flag: disabled stdout
IsLogTrace             = 1  # Trace[errorlog]: output detailed trace for Log-actions
IsTmpClean             = 1  # Flag: clean temp-folder
IsPublic               = 1  # Flag: Public application
IsFuture               = 0  # Flag: opens inactive future menu items
IsDemo                 = 0  # Flag: sets demo-mode (inactive)
IsNoEmail              = 1  # Flag: don't send email
IsPageClosed           = 0  # Flag: page is closed or moved to another address (page_redirect)
IsFlushOutput          = 0  # Flag: flush stdout
IsShowLoader           = 0  # Flag: sets page loader show enabled


LOCAL_FULL_TIMESTAMP   = '%d-%m-%Y %H:%M:%S'
LOCAL_EXCEL_TIMESTAMP  = '%d.%m.%Y %H:%M:%S'
LOCAL_EASY_TIMESTAMP   = '%d-%m-%Y %H:%M'
LOCAL_RUS_DATESTAMP    = '%d-%m-%Y'
LOCAL_EASY_DATESTAMP   = '%Y-%m-%d'
LOCAL_EXPORT_TIMESTAMP = '%Y%m%d%H%M%S'
UTC_FULL_TIMESTAMP     = '%Y-%m-%d %H:%M:%S'
UTC_EASY_TIMESTAMP     = '%Y-%m-%d %H:%M'
DATE_TIMESTAMP         = '%d/%m'
DATE_STAMP             = '%Y%m%d'

default_print_encoding = 'cp866'
default_unicode        = 'utf-8'
default_encoding       = default_unicode #'cp1251'
default_iso            = 'ISO-8859-1'

PUBLIC_URL = 'http://192.168.0.91:5000/'

TIMEZONE = 'Europe/Moscow'
TIMEZONE_COMMON_NAME = 'Moscow'


DEFAULT_ROOT = {
    'local'  : 'http://127.0.0.1:5000/',
    'public' : '',
}

LOG_PATH = './logs'
LOG_NAME = 'app'

page_redirect = {
    'items'    : ('*',),
    'base_url' : '/auth/onservice',
    'logins'   : ('admin',),
    'message'  : 'Waiting 30 sec',
}

###default_system_locale  = 'en_US.UTF-8'
default_system_locale  = 'ru_RU.UTF-8'

n_a = 'n/a'
cr = '\n'


class BaseConfiguration:
    DEBUG = False
    #SQLALCHEMY_ENGINE_OPTIONS = {'encoding': 'utf8'}
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SECRET_KEY = os.environ.get('SECRET_KEY')
    UPLOAD_FOLDER = 'uploads'
    TESTING = False
    LOGIN_DISABLED = False
    USE_SESSION_FOR_NEXT = True


class DevelopmentConfig(BaseConfiguration):
    DEBUG = True
    LANGUAGES = ['ru', 'en']
    SQLALCHEMY_ECHO = True
    JSON_SORT_KEYS = False
    ALLOWED_EXTENSIONS = {'txt', 'json', 'odt', 'pdf'}
    #SQLALCHEMY_ENGINE_OPTIONS = {'encoding': 'utf8'}
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEVELOPMENT_DATABASE_URL')
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'secret word' #'рекрут-тестирование-анкета'
    PLACE = 'КСА ВК-МО Одинцово 1435'
    PLACE_PARENT = 'КСА ВКС Московская область'
    PLACE_SVG_LABEL = '#_Odintsovo'


class ProductionConfig(BaseConfiguration):
    DEBUG = False
    JSON_SORT_KEYS = False
    #SQLALCHEMY_ENGINE_OPTIONS = {'encoding': 'utf8'}
    SQLALCHEMY_TRACK_MODIFICATIONS = False


config = { \
    'production' : ProductionConfig,
    'default'    : DevelopmentConfig,
}

DEFAULT_CONFIG = 'default'


##  --------------------------------------- ##

def isIterable(v):
    return not isinstance(v, str) and isinstance(v, Iterable)

def print_to(f, v, mode='ab', request=None, encoding=default_encoding):
    if IsDisableOutput:
        return
    items = not isIterable(v) and [v] or v
    if not f:
        f = getErrorlog()
    fo = open(f, mode=mode)
    def _out(s):
        if not isinstance(s, bytes):
            fo.write(s.encode(encoding, 'ignore'))
        else:
            fo.write(s)
        fo.write(cr.encode())
    for text in items:
        try:
            if IsDeepDebug:
                print(text)
            if request is not None:
                _out('%s>>> %s [%s]' % (cr, datetime.datetime.now().strftime(UTC_FULL_TIMESTAMP), request.url))
            _out(text)
        except Exception as e:
            pass
    fo.close()

def print_exception(stack=None):
    print_to(errorlog, '%s>>> %s:%s' % (cr, datetime.datetime.now().strftime(LOCAL_FULL_TIMESTAMP), cr))
    traceback.print_exc(file=open(errorlog, 'a'))
    if stack is not None:
        print_to(errorlog, '%s>>> Traceback stack:%s' % (cr, cr))
        traceback.print_stack(file=open(errorlog, 'a'))

def getErrorlog():
    return errorlog

def getCurrentDate():
    return datetime.datetime.now().strftime(LOCAL_EASY_DATESTAMP)
