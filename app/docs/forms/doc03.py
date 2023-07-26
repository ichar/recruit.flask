# -*- coding: utf-8 -*-

__all__ = ['render']

import random

from app.utils import getToday, getUserShortName

from . import get_data, today


#   -------------------------------------------------------------
#   Список лиц, имеющих склонность к девиантному поведению и(или) 
#   неудовлетворительную нервно-психологическую устойчивость
#   -------------------------------------------------------------


DEFAULT_DOC03_ROWS_COUNT = 10

def get_random():
    return str(random.choice([0,1]) and round(random.uniform(0.0, 9.0), 2) or '')


class PersonDoc03:
    def __init__(self, person):
        self.person = getUserShortName(person['name'])
        self.birthday = person['date']
        self.date = today()
        self.p1 = get_random()
        self.p2 = get_random()
        self.note = ''


class Doc03:

    def __init__(self, count=0):
        self.count = count or DEFAULT_DOC03_ROWS_COUNT

    def generate(self, data):
        rows = [PersonDoc03(data[i]) for i in range(self.count - 1)]
        return rows


def render(mode, **kw):
    if mode != 'doc03':
        return {}

    args = kw.get('args')

    data = get_data(f'{mode}.json')
    persons_count = 'persons' in data and len(data['persons']) or 0
    period = args.get('period')

    doc = Doc03(persons_count)

    # Формат листа печати
    orientation = 'portrait'

    return {
        'orientation' : orientation,
        'rows' : doc.generate(data['persons']),
        'doctor' : 'Ибрагимова Сулейма Рамизовна',
    }
