# -*- coding: utf-8 -*-

__all__ = ['render']

import random

from app.settings import g

from . import get_data


#   -----------------------------------------------------------------
#   ЛИСТ УЧЕТА РЕЗУЛЬТАТОВ РПРОФЕССИОНАЛЬНОГО ПСИХОЛОГИЧЕСКОГО ОТБОРА
#   -----------------------------------------------------------------


DEFAULT_DOC05_GROUPS_COUNT = 2

def get_random_int():
    return '%2d' % random.choice([-1, 0, 1])

def get_random_float(n=2):
    return str(random.choice([0,1]) and round(random.uniform(0.0, 9.0), n) or 0)


class Row1:
    def __init__(self, data, group, row):
        self.prop1 = data.get('prop1')
        self.prop2 = data.get('prop2')
        self.p3_1 = get_random_float()
        self.p3_2 = get_random_float()
        self.p4_1 = get_random_int()
        self.p4_2 = get_random_int()
        self.p5 = get_random_float()


class Row2:
    def __init__(self, data, group, row):
        self.prop3 = data.get('prop3')
        self.p7 = get_random_float()
        self.p8_1 = get_random_float()
        self.p8_2 = get_random_float()
        self.p8_3 = get_random_float()
        self.p8_4 = get_random_float()
        self.p8_5 = get_random_float()


class Group:
    def __init__(self, data, group):
        self.caption = data.get('caption')
        if group == 0:
            self.rows = [Row1(row, group, i) for i, row in enumerate(data.get('rows'))]
        else:
            self.rows = [Row2(row, group, i) for i, row in enumerate(data.get('rows'))]


class Doc05:
    def __init__(self, person):
        self.groups = []
        self.count = 0

    def generate(self, data):
        self.count = len(data) or DEFAULT_DOC05_GROUPS_COUNT
        self.groups = [Group(data[i], i) for i in range(self.count)]


def render(mode, **kw):
    if mode != 'doc05':
        return {}

    args = kw.get('args')
    persons = kw.get('persons')

    data = get_data(f'{mode}.json')

    # Selected Person item by uid
    # ---------------------------

    # [param:person] Призывник
    person_uid = args.get('person_uid')
    person = persons.search_by_uid(person_uid)

    args['person'] = person

    #g.default_index = 0

    doc = Doc05(person)
    doc.generate(data['groups'])

    # Тестовая батарея (список)
    battery_name = 'КОТ-3, СЭ-2'
    #battery_name = ', '.join([x.prop1 for x in doc.group[0]])

    # Формат листа печати
    orientation = 'portrait'

    return {
        'orientation' : orientation,
        'person' : person,
        'groups' : doc.groups,
        'battery_name' : battery_name,
    }

