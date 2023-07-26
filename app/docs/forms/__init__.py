# -*- coding: utf-8 -*-

import os
import json
import pdfkit
from copy import deepcopy
from operator import itemgetter

from flask_log_request_id import current_request_id
from flask import request, flash, g, session, current_app

from config import (
   basedir, IsPrintExceptions, print_exception, print_to, default_unicode
   )

from app.settings import (
   get_request_item, maketext, DEFAULT_DATE_FORMAT, DEFAULT_UNDEFINED
   )

from app.utils import (
   getUserShortName, getParsedDate, getDate, getToday, sortedDict,
   LifoStack
   )

DEFAULT_PERSONS_ROWS_COUNT = 10
DEFAULT_SPECIALITIES_ROWS_COUNT = 15
DEFAULT_REGIONS_ROWS_COUNT = 89
DEFAULT_REGIONS_MAX_LEVEL = 1

default_date_format = DEFAULT_DATE_FORMAT[1]


#   ------------------


def today():
    return getDate(getToday(), default_date_format)


def get_data(data_file_path):
    p = os.path.join(basedir, 'app/docs/data', data_file_path)
    f = open(p)
    data = json.load(f)

    return data


#   -----------------
#   Общие определения
#   -----------------

class EventDate():
    
    def __init__(self, date):
        day, month, year = getParsedDate(date, as_list=True)
        self.day = day
        self.month = month
        self.year = year
        self.YY = year[-2:]


class Region:

    def __init__(self, index, uid, region):
        if region and isinstance(region, dict):
            if uid == region['uid'] and index == region['index']:
                self.index = index
                self.uid = uid
                self.level = region['level']
                self.name = region['name']
                self.center = region['center']
        else:
            self.index = index
            self.uid = uid
            self.level = -1
            self.name = maketext('All regions')
            self.center = 0


class Regions:

    def __init__(self, count=0):
        self.count = count or DEFAULT_REGIONS_ROWS_COUNT
        self._items = []

    def generate(self, data):
        self._items = []
        for i, uid in enumerate(list(data.keys())):
            item = None
            if i < self.count:
                item = Region(i+1, uid, data[uid])
            if item and item.uid:
                self._items.append(item)
        self._items.insert(0, Region(0, '0', None))

    @property
    def items(self):
        return self._items

    def search_by_uid(self, uid):
        for item in self._items:
            if uid == item.uid:
                return item
        return None

    def get_by_level(self, level, uid=None):
        items = []
        for item in self._items:
            if level == item.level and ((not uid and level == 0) or (uid and item.uid.startswith(uid) and item.uid > uid)):
                items.append(item)
        return items

    def tree(self, level=0, index=0, output=[]):
        item = self._items[index]
        items = self.get_by_level(level, uid=item.uid)
        if items or item.center:
            output.append((item, items))
        if items:
            for item in items:
                if item.level < DEFAULT_REGIONS_MAX_LEVEL+1:
                    self.tree(level=item.level+1, index=item.index, output=output)


class Person:

    def __init__(self, uid, person):
        if person and isinstance(person, dict):
            self.uid = uid
            self.name = person['name']
            self.short_name = getUserShortName(person['name'])
            self.full_name = person['name']
            self.date = person['date']
            self.birthday = self.date
            self.kind = ''
            self.team = ''
            self.status = person['status']
        else:
            self.uid = DEFAULT_UNDEFINED
            self.person = ''
            self.short_name = maketext('Check person')


class Persons:

    def __init__(self, count=0):
        self.count = count
        self._items = []

    def generate(self, data):
        self._items = [Person(uid, data[uid]) for i, uid in enumerate(data.keys()) if i < self.count]
        self._items.insert(0, Person('', None))
        return self

    @property
    def items(self):
        return self._items

    def search_by_uid(self, uid):
        for item in self._items:
            if uid == item.uid:
                return item
        return None


class Speciality:

    def __init__(self, index, number, item):
        self.index = str(index)
        self.number = str(number)
        self.title = item['title']
        self.classes = item['classes']


class Specialities:

    def __init__(self, count=0):
        self.count = count
        self._items = []

    def generate(self, data):
        items = sortedDict(data) #sorted(data, key=itemgetter('title'))
        keys = list(items.keys())
        self._items = [Speciality(i+1, key, data[key]) for i, key in enumerate(keys) if i < self.count]
        ob = {
             'title' : maketext('All specialities'),
             'classes' : ''
             }
        self._items.insert(0, Speciality(0, '000', ob))

    @property
    def items(self):
        return self._items
    @property
    def sorted_by_index(self):
        return sorted(self._items, key=lambda x: x.index)

    def get_by_index(self, index):
        items = self.sorted_by_index
        return index < len(items)+1 and items[index] or None

    def search_by_index(self, index):
        i = int(index)
        if i < len(self._items):
            return self._items[i]
        return None

    def search_by_number(self, number):
        for item in self._items:
            if number == item.number:
                return item
        return None


class Region:

    def __init__(self, index, uid, region):
        if region and isinstance(region, dict):
            if uid == region['uid'] and index == region['index']:
                self.index = str(index)
                self.uid = uid
                self.level = region['level']
                self.name = region['name']
                self.center = region['center']
        else:
            self.index = str(index)
            self.uid = uid
            self.level = -1
            self.name = maketext('All regions')
            self.center = 0
        self.is_child = []


class Regions:

    def __init__(self, count=0):
        self.count = count or DEFAULT_REGIONS_ROWS_COUNT
        self._items = []

    def generate(self, data):
        self._items = []
        for i, uid in enumerate(list(data.keys())):
            item = None
            if i < self.count:
                item = Region(i+1, uid, data[uid])
            if item and item.uid:
                self._items.append(item)
        self._items.insert(0, Region(0, '0', None))

    @property
    def items(self):
        return self._items
    @property
    def sorted_by_index(self):
        return sorted(self._items, key=lambda x: x.index)
    @property
    def sorted_by_uid(self):
        return sorted(self._items, key=lambda x: x.uid)

    def search_by_uid(self, uid):
        for item in self._items:
            if uid == item.uid:
                return item
        return None

    def get_by_index(self, index):
        items = self.sorted_by_uid
        return index < len(items)+1 and items[index] or None

    def get_by_level(self, level, uid=None):
        items = []
        for item in self._items:
            if level == item.level and ((not uid and level == 0) or (uid and item.uid.startswith(uid) and item.uid > uid)):
                items.append(item)
        return items

    def tree(self):
        items = deepcopy(sorted(self._items, key=lambda x: x.uid))

        def _check_level(item, parent):
            li = len(item.uid)
            lp = len(parent)
            return li, lp

        def _set_child(pitem, x, n):
            if pitem:
                if x == 1 and -1 in pitem.is_child:
                    pass
                elif x not in pitem.is_child:
                    pitem.is_child.append(x)
                    n += 1
            return n

        def _down(item, pitem, parent, level, n1):
            stack.push((parent, level))
            parent = item.uid
            level = item.level
            n1 = _set_child(pitem, 1, n1)
            return parent, level, n1

        def _up(pitem, n2):
            parent, level = stack.pop()
            n2 = _set_child(pitem, -1, n2)
            return parent, level, n2

        stack = LifoStack()
        parent = ''
        item = None
        pitem = None
        level = -1
        n1, n2 = 0, 0

        for item in items:
            li, lp = _check_level(item, parent)
            if li > lp:
                parent, level, n1 = _down(item, pitem, parent, level, n1)
                is_check = 0
            elif li < lp:
                parent, level, n2 = _up(pitem, n2)
                li, lp = _check_level(item, parent)
                is_check = 1
            if is_check:
                if li == lp and level == item.level:
                    parent, level, n1 = _down(item, pitem, parent, level, n1)
                    n2 = _set_child(pitem, -1, n2)
                    is_check = 1

            pitem = item

        if n1 > n2:
            item = Region(0, '', None)
            item.is_child = [-1]
            item.name = ''

            for n in range(0, n1-n2):
                items.append(item)

        return items


#   ------------------


def check_request():
    reporttype = get_request_item('reporttype') or 'index'

    date_from = get_request_item('date_from') or today() #getDate(getDateOnly(getToday()), LOCAL_EASY_DATESTAMP)
    date_to = get_request_item('date_to') or date_from

    if date_from != date_to:
        period = '%s %s %s %s %s' % (maketext('for period'), maketext('from'), date_from, maketext('to'), date_to)
    else:
        period = '%s %s' % (maketext('for date'), date_from)

    person_uid = get_request_item('person_uid') or None

    speciality_index = get_request_item('speciality_index') or ''

    region_index = get_request_item('region_index') or ''

    args = {
        'reporttype' : reporttype,
        'date_from' : (None, date_from),
        'date_to': (None, date_to),
        'person_uid' : person_uid,
        'speciality_index' : speciality_index,
        'region_index' : region_index,
        'period' : period,
    }

    return args


def get_persons():
    persons = None
    data = get_data('persons.json')
    if 'persons' in data:
        obs = data['persons']
        count = len(obs.keys()) or DEFAULT_PERSONS_ROWS_COUNT
        persons = Persons(count)
        persons.generate(obs)

    return persons


def get_specialities():
    specialities = None
    data = get_data('specialities.json')
    if 'items' in data:
        obs = data['items']
        count = len(obs.keys()) or DEFAULT_SPECIALITIES_ROWS_COUNT
        specialities = Specialities(count)
        specialities.generate(obs)

    return specialities


def get_regions():
    regions = None
    data = get_data('regions.json')
    if 'regions' in data:
        obs = data['regions']
        count = len(obs.keys()) or DEFAULT_REGIONS_ROWS_COUNT
        regions = Regions(count)
        regions.generate(obs)

    return regions


def makepdf(body, **kw):
    #
    # Wkhtmltopdf python wrapper to convert html to pdf using the webkit rendering engine and qt:
    #   https://pypi.org/project/pdfkit/
    # Installation:
    # $ sudo apt-get install wkhtmltopdf
    # $ pip install pdfkit
    #
    with_pdf = kw.get('with_pdf') or 0

    if not with_pdf:
        return None

    mode = kw.get('mode')

    options = {
        'page-size' : 'Legal',
        'orientation' : kw.get('orientation', 'portrait'),
        'margin-top' : '0.75in',
        'margin-bottom' : '0.75in',
        'margin-left' : '0.50in',
        'margin-right' : '0.50in',
        'encoding' : 'UTF-8',
        #'enable_local_file_access': False,
        #'print_media_type' : False,
        #'title' : context_dict.get('title', 'PDF'),
    }

    try:
        #configuration = pdfkit.configuration()
        if with_pdf == 1:
            # Формирование и возврат контента html(body)->pdf
            output_path = False
    
            return pdfkit.from_string(body, #.encode(default_unicode), 
                options=options, 
                #configuration=configuration
                )
        elif with_pdf == 2:
            # Печать pdf в файл
            request_id = current_request_id()
            output_path = '%s/app/static/files/%s-%s.pdf' % (basedir, request_id, mode)
    
            pdfkit.from_string(body, #.encode(default_unicode), 
                output_path=output_path, 
                options=options, 
                #configuration=configuration
                )
    except:
        if IsPrintExceptions:
            print_exception()

    return None
    

## ==================================================== ##
