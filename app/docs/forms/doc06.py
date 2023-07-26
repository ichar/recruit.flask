# -*- coding: utf-8 -*-

__all__ = ['render']

import random

from app.settings import current_user
from app.utils import getUserShortName

from . import get_data, today


#   ---------------------------------------------------------------
#   Ведомость результатов профессионального психологического отбора
#   ---------------------------------------------------------------


DEFAULT_DOC06_ROWS_COUNT = 10

def get_random():
    return str(random.choice([0,1]) and round(random.uniform(0.0, 9.0), 1) or 0)


class PersonDoc06:
    def __init__(self, person):
        self.person = getUserShortName(person['name'])
        self.birthday = person['date']
        self.date = today()
        self.OPS = get_random()
        self.NPU = get_random()
        self.NVS = get_random()
        self.SDP = get_random()
        for x in ('KCBTO'):
            setattr(self, x, get_random())
        self.SE = get_random()
        self.NPUA = get_random()
        self.SE = get_random()
        self.VUZ = get_random()
        for x in ('KCBTO'):
            setattr(self, '%sX' % x, get_random())
        self.info = ''


class Doc06:

    def __init__(self, count=0):
        self.count = count or DEFAULT_DOC06_ROWS_COUNT

    def generate(self, data):
        rows = [PersonDoc06(data[i]) for i in range(self.count - 1)]
        return rows


def render(mode, **kw):
    if mode != 'doc06':
        return {}

    args = kw.get('args')

    data = get_data(f'{mode}.json')
    persons_count = 'persons' in data and len(data['persons']) or 0
    period = args.get('period')

    doc = Doc06(persons_count)

    # Формат листа печати
    orientation = 'landscape'

    return {
        'orientation' : orientation,
        'rows' : doc.generate(data['persons'])
    }
