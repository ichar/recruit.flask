# -*- coding: utf-8 -*-

__all__ = ['render']

import random
from copy import deepcopy

from app.settings import DEFAULT_DOCS_MINUS
from app.utils import getToday, getUserShortName

from . import get_data, today


#   -----------------------------------------------
#   Лист учета результатов профессионального отбора
#   -----------------------------------------------

with_total_column = -1


DEFAULT_DOC16_ROWS_COUNT = 20
DEFAULT_DOC16_ITEMS = 4
DEFAULT_DOC16_TOTAL = 3
DEFAULT_DOC16_MAX_VALUES = (0,0,10,4)

def get_random(max_value=10):
    return random.choice(range(1, max_value+1))


class Doc16:

    def __init__(self, count=0):
        self.count = count or DEFAULT_DOC16_ROWS_COUNT
        self.rows = []

    def generate(self, data):
        for index, row in enumerate(data['rows']):
            if row and isinstance(row, dict) and index == row.get('index'):
                items = row.get('items')
                if items:
                    values = row.get('values')
                    if values:
                        x = values.split('-')
                        if x and len(x) == 2:
                            start = int(x[0])
                            finish = int(x[1])
                            numbers = list(range(start, finish+1))
                            for n in numbers:
                                max_value = DEFAULT_DOC16_MAX_VALUES[n]
                                value = get_random(max_value)
                                items.append({'col': n, 'item': value})
                            if with_total_column > -1:
                                total = sum([x.get('item', 0) for x in items if 'item' in x and (isinstance(x['item'], int) or not x['item'])])
                                items.insert(DEFAULT_DOC16_TOTAL, {'col': finish-start+1, 'item': total})
                    for n, item in enumerate(items):
                        if not item:
                            continue
                        item['cls'] = '%s c%s' % (item and item.get('cls') or '', n)

                self.rows.append(deepcopy(row))


def render(mode, **kw):
    if mode != 'doc16':
        return {}

    args = kw.get('args')
    persons = kw.get('persons')

    data = get_data(f'{mode}.json')
    period = args.get('period')

    # Selected Person item by uid
    # ---------------------------

    # [param:person] Призывник
    person_uid = args.get('person_uid')
    person = persons.search_by_uid(person_uid)

    args['person'] = person

    doc = Doc16()
    doc.generate(data)

    # Формат листа печати
    orientation = 'portrait'

    return {
        'orientation' : orientation,
        'person' : person,
        'rows' : doc.rows,
    }
