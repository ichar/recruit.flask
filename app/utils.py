# -*- coding: utf-8 -*-

import os
import locale
import decimal
import datetime
import time
import re
import random
import string
from collections import Iterable
import io
from sortedcontainers import SortedDict
import base64
import codecs
import zipfile
from queue import LifoQueue


from config import (
     basedir, IsDebug, IsDeepDebug, IsPrintExceptions, default_print_encoding, default_unicode, default_encoding, default_iso, cr,
     LOCAL_FULL_TIMESTAMP, LOCAL_EASY_TIMESTAMP, UTC_EASY_TIMESTAMP, DATE_STAMP,
     print_to, print_exception
)

_MAX_TITLE_WORD_LEN = 50
_WEEKDAYS_DATESTAMP = '%d/%b/%Y'

empty_value = '...'


##  ============
##  System Utils
##  ============


class LifoStack:
    
    def __init__(self, maxsize=0):
        self._stack = LifoQueue(maxsize=maxsize)
    
    def push(self, item):
        self._stack.put(item)
        return item

    def pop(self):
        item = None
        if not self._stack.empty():
            item = self._stack.get()
        return item


class SystemConfig:

    def __init__(self):
        now = getDate(getToday(), format=DATE_STAMP)

    def __getattr__(self, name):
        try:
            return self.__getattribute__(name)
        except:
            return None

    def get(self, name, default=None):
        v = getattr(self, name)
        if v is None:
            return default
        return v


def make_config(source, encoding=default_encoding):
    config = SystemConfig()

    with open(os.path.join(basedir, source), 'r', encoding=encoding) as fin:
        for line in fin:
            s = line
            if line.startswith(';') or line.startswith('#'):
                continue
            x = line.split('::')
            if len(x) < 2:
                continue

            key = x[0].strip()
            value = x[1].strip()

            if not key:
                continue
            elif not value:
                value = None
            elif '|' in value:
                value = list(filter(None, value.split('|')))
            elif value.lower() in 'false:true':
                value = True if value.lower() == 'true' else False
            elif value.isdigit():
                value = int(value)
            elif key in ':console:':
                value = normpath(os.path.join(basedir, value))

            setattr(config, key, value)

    return config


# -----------------


def getBOM(encoding):
    return codecs.BOM_UTF8.decode(encoding)


def show_imported_modules():
    return [x for x in _imports()]


def os_exec(command, message):
    try:
        code = os.system(command)
        if code:
            raise Exception('%s, command: %s, code: %s' % (message, command, code))
    except:
        raise


def mkdir(name):
    os_exec(os.name == 'posix' and 
        'mkdir "'+name+'"' or 
        'mkdir "'+name+'"', 
        'Error while create a folder: %s' % name)

create_folder = mkdir

def rmdir(name):
    os_exec(os.name == 'posix' and 
        "rm -rf '%s'" % name or 
        'rmdir /s/q "%s"' % name, 
        'Error while remove a folder: %s' % name)

remove_folder = rmdir

def del_file(name, check=True):
    if check and not os.path.exists(name):
        return
    os_exec(os.name == 'posix' and 
        "rm -f '%s'" % name or 
        'del /f "%s"' % os.path.normpath(name), 
        'Error while remove a file: %s' % name)

remove_file = del_file

def mv_file(path_from, path_to):
    os_exec(os.name == 'posix' and 
        'mv '+path_from+' '+path_to or 
        'move /Y "'+os.path.normpath(path_from)+'" "'+os.path.normpath(path_to)+'"', 
        'Error while moving a file from: %s to: %s' % (path_from, path_to))

move_file = mv_file

def cp_file(path_from, path_to):
    os_exec(os.name == 'posix' and 
        'cp '+path_from+' '+ path_to or 
        'copy /Y /V "'+os.path.normpath(path_from)+'" "'+os.path.normpath(path_to)+'"', 
        'Error while copying a file from: %s to: %s' % (path_from, path_to))

copy_file = cp_file


def normpath(p, share=None):
    if p.startswith('//'):
        return (not share and '//%s' or r'\\%s') % re.sub(r'\\', '/', os.path.normpath(p[2:]))
    return re.sub(r'\\', '/', os.path.normpath(p))


def check_folder_exists(destination, root):
    folders = destination.replace(root, '').split('/')
    folder = root
    while len(folders) > 0:
        name = folders.pop(0)
        if not name:
            continue
        folder = normpath(os.path.join(folder, name), 1)
        if not (os.path.exists(folder) and os.path.isdir(folder)):
            mkdir(folder)


def unzip(src, destination=None, is_relative=False):
    if not os.path.exists(src):
        return
    if not destination:
        destination = os.path.split(src)[0]
    elif is_relative:
        destination = os.path.join(os.path.split(src)[0], destination)
    x = zipfile.ZipFile(src, 'r')
    x.extractall(destination)
    x.close()


def fromtimestamp(value):
    return datetime.datetime.fromtimestamp(value)


def getToday():
    return datetime.datetime.now()


def getTime(format=UTC_EASY_TIMESTAMP):
    return getToday().strftime(format)


def getDate(value, format=UTC_EASY_TIMESTAMP, is_date=False):
    if is_date:
        try:
            return value and datetime.datetime.strptime(value, format) or None
        except:
            return None
    else:
        return value and value.strftime(format) or ''


def getDateOnly(value, format=DATE_STAMP):
    return datetime.datetime.strptime(value.strftime(format), format)


def getTimestamp():
    return str(datetime.datetime.timestamp(getToday())).replace('.', '')


def getTimedelta(date, x):
    #
    #   Returns timedelta between two dates in seconds
    #
    p = 0
    if isinstance(x, int):
        p = date - datetime.timedelta(x)
    else:
        p = date - x
    if isinstance(p, datetime.timedelta): 
        return p.total_seconds() * 1000
    elif isinstance(p, datetime.datetime):
        return p.timestamp() * 1000
    return p


def parse_month(name):
    monthes = {
        'January' : 'Января',
        'February' : 'Февраля',
        'March'  : 'Марта',
        'April' : 'Апреля',
        'May'  : 'Мая',
        'June' : 'Июня',
        'July' : 'Июля',
        'August' : 'Августа',
        'September' : 'Сентября',
        'October' : 'Октября',
        'November' : 'Ноября',
        'December' : 'Декабря',
    }
    return monthes.get(name) or name


def getParsedDate(value, as_list=None, month_length=10, as_html=True):
    day, month, year = value.strftime('%d-%B-%Y').split('-')
    month = str.center(parse_month(month).lower(), month_length)
    if as_html:
        month = month.replace(' ', '&nbsp;')
        day = '«&nbsp;%s&nbsp;»' % day
        year = '%s&nbsp;г.' % year
    return as_list and (day, month, year) or '%s %s %s' % (day, month, year)


def isTimedelta(date, x):
    #
    #   Checked timedelta with given date and number or another date in seconds
    #
    if isinstance(x, int):
        return date.timestamp() * 1000 > x
    if isinstance(x, datetime.datetime):
        return date > x
    return False


def getUID(size=2):
    return getTimestamp()+''.join([random.choice(string.ascii_letters + string.digits) for n in range(size)])


def spent_time(start, finish=None):
    if not finish:
        finish = datetime.datetime.now()
    t = finish - start
    return (t.seconds*1000000+t.microseconds)/1000000


def worder(value, length=None, comma=None):
    max_len = (not length or length < 0) and _MAX_TITLE_WORD_LEN or length
    words = value.split()
    s = ''
    changed = 0
    while len(words):
        word = words.pop(0).strip()
        if s:
            s += ' '
        if len(word) <= max_len:
            s += word
        else:
            w = word[max_len:]
            if comma and comma in w:
                words = ['%s%s%s' % (x.strip(), comma, ' ') for x in w.split(comma)] + words
            else:
                words.insert(0, w)
            s += word[:max_len]
            changed = 1
    s = s.strip()
    if comma and s.endswith(comma):
        s = s[:-1]
    return changed, s


def splitter(value, length=None, comma=','):
    if value and len(value) > (length or _MAX_TITLE_WORD_LEN):
        changed, v = worder(value, length=length, comma=comma in value and comma)
        return v
    return value


def out(x):
    return x.encode(default_print_encoding, 'ignore')


def cdate(date, fmt=LOCAL_FULL_TIMESTAMP):
    if date:
        return str(date.strftime(fmt))
    return empty_value


def clean(value):
    return value and re.sub(r'[\n\'\"\;\%\*]', '', value).strip() or ''


def cleanHtml(value, without_point=None):
    return value and re.sub(r'\s+', ' ', re.sub(r'<.*?>', '', without_point and value.endswith('.') and value[:-1] or value)) or ''


def xsplit(value, keys, is_list=None):
    out = [value]
    for s in keys:
        for n in range(len(out)):
            v = out.pop(0)
            out += [x.strip() for x in v.split(s)]
    return is_list and out or list(set(out))


def is_unique_strings(v1, v2, keys=' ,.;'):
    x1 = xsplit(v1, keys)
    x2 = xsplit(v2, keys)
    return [x for x in x2 if x not in x1] and True or False


def usplitter(values, keys):
    items = []
    for x in values:
        items += xsplit(x, keys)
    return list(set(items))

default_indent = ' '*2

def isIterable(v):
    return not isinstance(v, str) and not isinstance(v, dict) and isinstance(v, Iterable)


def makeCSVContent(rows, title, IsHeaders, **kw):
    encoding = kw.get('encoding') or default_encoding
    output = io.BytesIO()
    
    crlf = '\r\n'
    eol = crlf.encode()

    for i, row in enumerate(rows):
        line = b''
        for j, column in enumerate(row):
            line += str(column).encode(encoding) + b';'
        output.write(line+eol)

    output.seek(0)

    return output.read()


def getParamsByKeys(params, keys):
    output = {}
    for param in params:
        if param['PName'] in keys:
            i = keys.index(param['PName'])
            key = keys.pop(i)
            output[key] = param
    return output


def getWhereFilter(filter, key, with_and=True):
    return '%s' % (
        filter and ("%s%s like '%%%s%%'" % (with_and and ' and ' or '', key, filter)) or '')


def makeIDList(ids):
    return ','.join([str(x) for x in sorted(ids)])


def checkPaginationRange(n, page, pages):
    return n < 3 or (n > page-3 and n < page+3) or n > pages-1


def monthdelta(date, delta):
    m, y = (date.month+delta) % 12, date.year + ((date.month)+delta-1) // 12
    if not m: m = 12
    d = min(date.day, [31,29 if y%4==0 and not y%400==0 else 28,31,30,31,30,31,31,30,31,30,31][m-1])
    return date.replace(day=d,month=m, year=y)


def daydelta(date, delta):
    return delta and date + datetime.timedelta(days=delta) or date


def minutedelta(date, delta):
    return delta and date + datetime.timedelta(minutes=delta) or date


def weeknumber(date, with_year=None):
    x = date.isocalendar()
    return '%s%02d' % (with_year and '%04d-' % x[0] or '', x[1])


def weekday(date):
    return date.isocalendar()[2]


def weekdays(week, year, fmt=_WEEKDAYS_DATESTAMP):
    begin = getDate('%s0101' % year, '%Y%m%d', is_date=True)
    delta = begin.isoweekday() > 4 and 1 or -1
    while True:
        if begin.isoweekday() == 1:
            break
        begin = daydelta(begin, delta)
    week_begin = (int(week) - 1) * 7
    s = daydelta(begin, 1 + week_begin - weekday(begin))
    e = daydelta(s, 6)
    return s.strftime(fmt), e.strftime(fmt)


def Capitalize(s, as_is=None):
    return (s and len(s) > 1 and s[0].upper() + (as_is and s[1:] or s[1:].lower())) or (len(s) == 1 and s.upper()) or ''


def unCapitalize(s, as_is=None):
    return (s and len(s) > 1 and s[0].lower() + s[1:]) or (len(s) == 1 and s.lower()) or ''


def getUserShortName(name):
    x = name.split(' ')
    l = len(x)
    if not l:
        return name
    surname = l and x[0]
    lastname = l > 2 and x[2] and ('%s.' % x[2][0].upper()) or ''
    firstname = l > 1 and x[1] and ('%s.' % x[1][0].upper()) or ''
    return '%s %s%s' % (surname, lastname, firstname)


def sortedDict(dic=None):
    return SortedDict(dic)


def reprSortedDict(dic, is_sort=False):
    items = []
    for key in (is_sort and sorted(dic) or dic):
        if dic[key]:
            items.append('%s=%s' % (key, dic[key]))
    return '{%s}' % ','.join(items)


def encode_base64(s, altchars=None, encoding=None):
    return base64.b64encode(isinstance(s, bytes) and s or bytes(s, encoding or default_unicode), altchars=altchars)


def decode_base64(s, altchars=None, validate=False):
    return s and base64.b64decode(s, altchars=altchars, validate=validate) or ''


def image_base64(src, image_type, size=None, image=None, optimize=None):
    from PIL import Image
    if image is None:
        with open(src, 'rb') as fi:
            image = fi.read()
    elif isinstance(image, str) and 'base64' in image:
        image = base64.b64decode(re.sub('^data:image/.+;base64,', '', image))
    if size:
        image = Image.open(io.BytesIO(image))
        image_size = image.size
        w, h = size
        if optimize:
            if image_size[0] >= image_size[1]:
                w, h = w[1], None
            else:
                w, h = w[0], None
        if w is None and h:
            w = int(image_size[0] / (image_size[1] / h))
        if h is None and w:
            h = int(image_size[1] / (image_size[0] / w))
        image = image.resize((w, h), Image.ANTIALIAS)
        format = image_type and image_type.lower() in ('png', 'gif') and image_type.upper() or 'JPEG'
        buffered = io.BytesIO()
        image.save(buffered, format=format, optimize=True, quality=95)
        encoded = base64.b64encode(buffered.getvalue())
    else:
        encoded = base64.b64encode(image)
    return 'data:image/%s;base64,%s' % (image_type or 'jpg', encoded.decode())


def rfind(s, sub, start=0):
    for n in range(-1, -len(s)-1, -1):
        x = s[start + n]
        if x == sub:
            return n
    return 0


def sjoin(values, separator=None):
    return (separator or '').join([str(x) for x in values])


def unquoted_url(s):
    """
        Decode UTF-8 encoded URL escaped bytes
    """
    from urllib.parse import unquote
    return unquote(s)


def getString(value, save_links=None, is_clean=None, with_html=None, without_html=None):
    s = value and re.sub(
        r'[\']', '', 
        re.sub(r'\"+?', not is_clean and '"' or '', 
        re.sub(r'\n{3,}', r'\n\n', 
        re.sub(r'\n[\s]+\n', r'\n\n', 
        value.strip()
        )))) or ''
    if with_html:
        s = re.sub(r'^\"(.*)\"$', r'\1', s)
    else:
        s = re.sub(r'([^<].*)\"(.*?)\"(.*[^>])', r'\1%s\2%s\3' % (chr(171), chr(187)), s)
    if without_html:
        s = re.sub(r'<.*?>', '', re.sub(r'<br>', r'\n', s))
    return not save_links and cleanLinks(s) or s


def getSQLString(value):
    v = value and value.replace('\\', '')
    return v and re.sub(r'([\'\"\;])', r'\\\1', v.strip()) or ''


def getHtmlString(value, save_links=None):
    return getString(value, save_links=save_links).replace('"', '&quot;')


def getHtmlCaption(value, html=None, **kw):
    eol = kw.get('cr') or cr
    try:
        s = value and '<br>'.join([checkLink(x, **kw) for x in value.split(eol)]).replace('\\', '') or ''
        return html and html % s or s
    except:
        raise
    return value


def getURLQueryString(url):
    x = url.split('?')
    return len(x) > 1 and '?%s' % x[1] or ''


def getSelectedItemByKey(items, key):
    index = -1
    for i, k in enumerate(items):
        if k == key:
            index = i
    return index > -1 and items[index] or None


