# -*- coding: utf-8 -*-

__all__ = ['render']

import random

from app.settings import g, DEFAULT_DOCS_MARKER

from app.utils import getToday, getUserShortName

from . import Person, get_data, today


#   ----------------------------------------------------
#   ЛИСТ РЕЗУЛЬТАТОВ СОЦИАЛЬНО-ПСИХОЛОГИЧЕСКОГО ИЗУЧЕНИЯ
#   ----------------------------------------------------


DEFAULT_DOC04_GROUPS_COUNT = 1

def get_random():
    return random.choice(range(10))

def set_index(group, subgroup, row):
    if group == 1 and subgroup == 0 and row == 0:
        g.default_index = 0
    g.default_index += 1


class PersonDoc04():
    
    def __init__(self, person):
        self = person
        self.p1 = get_random()
        self.p2 = get_random()
        self.p3 = get_random()
        self.p4 = get_random()
        self.p5 = get_random()
        self.p6 = get_random()
        self.p7 = get_random()
        self.education = 'среднее-специальное'
        self.vus = '25-349287-AB'
        self.info = 'слесарь-механик'
        self.signer = 'старший инспектор Иванов А.А.'
        self.location = 'Р.Ф. Московская обл., г. Одинцово'


class Doc04:

    def __init__(self, person):
        self.person = person

    def generate(self, data):
        return PersonDoc04(self.person)


def render(mode, **kw):
    if mode != 'doc04':
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

    g.default_index = 0

    doc = Doc04(person)
    doc.generate(data)

    # Формат листа печати
    orientation = 'portrait'

    return {
        'orientation' : orientation,
        'person' : doc.person,
    }

