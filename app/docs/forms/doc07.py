# -*- coding: utf-8 -*-

__all__ = ['render']

import random
from copy import deepcopy

from app.settings import DEFAULT_DOCS_MINUS
from app.utils import getToday, getUserShortName

from . import get_data, today


#   -------------------------------------------------------------
#   Результаты профессионального психологического отбора граждан, 
#   первоначально поставленных на воинский учет
#   -------------------------------------------------------------


DEFAULT_DOC07_ROWS_COUNT = 14
DEFAULT_DOC07_ITEMS = 4
DEFAULT_DOC07_TOTAL = 4

def get_random():
    return random.choice(range(10))


class Doc07:

    def __init__(self, count=0):
        self.count = count or DEFAULT_DOC07_ROWS_COUNT
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
                                value = get_random()
                                items.append({'col': n, 'item': value})
                            total = sum([x.get('item', 0) for x in items if 'item' in x and (isinstance(x['item'], int) or not x['item'])])
                            items.insert(DEFAULT_DOC07_TOTAL, {'col': 4, 'item': total})
                    for n, item in enumerate(items):
                        if not item:
                            continue
                        item['cls'] = '%s c%s' % (item and item.get('cls') or '', n)

                self.rows.append(deepcopy(row))


def render(mode, **kw):
    if mode != 'doc07':
        return {}

    args = kw.get('args')

    data = get_data(f'{mode}.json')
    period = args.get('period')

    doc = Doc07()
    doc.generate(data)

    # Формат листа печати
    orientation = 'portrait'

    return {
        'orientation' : orientation,
        'rows' : doc.rows,
    }
