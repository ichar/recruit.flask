# -*- coding: utf-8 -*-

__all__ = ['render']

import random

from app.utils import getUserShortName

from . import get_data, today


#   ----------------------------------------------
#   ВЕДОМОСТЬ РЕЗУЛЬТАТОВ ПРОФЕССИОНАЛЬНОГО ОТБОРА
#   ----------------------------------------------


DEFAULT_DOC01_ROWS_COUNT = 10

def get_random():
    return str(random.choice([0,1]) and round(random.uniform(0.0, 9.0), 2) or 0)


class PersonDoc01:
    def __init__(self, person):
        self.person = getUserShortName(person['name'])
        self.birthday = person['date']
        self.date = today()
        self.kind = ''
        self.team = ''
        self.status = person['status']
        for x in ('KCOBTP'):
            setattr(self, x, get_random())


class Doc01:

    def __init__(self, count=0):
        self.count = count or DEFAULT_DOC01_ROWS_COUNT

    def generate(self, data):
        rows = [PersonDoc01(data[i]) for i in range(self.count - 1)]
        return rows


def render(mode, **kw):
    if mode != 'doc01':
        return {}

    args = kw.get('args')

    data = get_data(f'{mode}.json')
    persons_count = 'persons' in data and len(data['persons']) or 0
    period = args.get('period')

    doc = Doc01(persons_count)

    # Формат листа печати
    orientation = 'landscape'

    return {
        'orientation' : orientation,
        'rows' : doc.generate(data['persons'])
    }
