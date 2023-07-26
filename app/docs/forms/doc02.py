# -*- coding: utf-8 -*-

__all__ = ['render']

import random

from app.settings import g, DEFAULT_DOCS_MARKER

from . import get_data


#   ----------------------------------------------------
#   ЛИСТ РЕЗУЛЬТАТОВ СОЦИАЛЬНО-ПСИХОЛОГИЧЕСКОГО ИЗУЧЕНИЯ
#   ----------------------------------------------------


DEFAULT_DOC02_GROUPS_COUNT = 2

def get_random():
    return random.choice([0,1])

def set_index(group, subgroup, row):
    if group == 1 and subgroup == 0 and row == 0:
        g.default_index = 0
    g.default_index += 1


class Row:
    def __init__(self, data, group, subgroup, row):
        self.prop = data.get('prop')
        self.plus = get_random()
        self.minus = not self.plus and get_random() or 0

        set_index(group, subgroup, row)

        self.index = g.default_index


class SubGroup:
    def __init__(self, data, group, subgroup):
        self.caption = data.get('caption')
        self.rows = [Row(row, group, subgroup, i) for i, row in enumerate(data.get('rows'))]


class Group:
    def __init__(self, data, group):
        self.caption = data.get('caption')
        self.subgroups = [SubGroup(row, group, i) for i, row in enumerate(data.get('rows'))]


class Doc02:
    def __init__(self, person):
        self.groups = []
        self.count = 0

    def generate(self, data):
        self.count = len(data) or DEFAULT_DOC02_GROUPS_COUNT
        self.groups = [Group(data[i], i) for i in range(self.count)]


def render(mode, **kw):
    if mode != 'doc02':
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

    doc = Doc02(person)
    doc.generate(data['groups'])

    # Формат листа печати
    orientation = 'portrait'

    return {
        'orientation' : orientation,
        'person' : person,
        'groups' : doc.groups,
        'marker' : DEFAULT_DOCS_MARKER,
    }

