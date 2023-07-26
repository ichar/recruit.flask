# -*- coding: utf-8 -*-

__all__ = ['render', 'get_specialities', 'Doc09']

import random
import numbers
from operator import itemgetter

from app.settings import DEFAULT_DOCS_MINUS, get_request_item, maketext
from app.utils import getToday, getUserShortName

from config import IsDeepDebug

from . import get_data, today, Region


#   --------------------------------------------------------
#   Сведения о  ходе отправки граждан, подготовленных по ВУС
#   --------------------------------------------------------


DEFAULT_DOC09_ROWS_COUNT = 10
DEFAULT_DOC09_ITEMS = 4
DEFAULT_DOC09_TOTAL = 3
DEFAULT_DOC09_DIGITS = 2
DEFAULT_DOC09_COLS_EXCLUDE = ('pregion','t11','t12','css')
DEFAULT_DOC09_COLS_TOTAL = ('t111','t121','t131','ptotal','ftotal',)
DEFAULT_DOC09_COLS_STATUS = ('t11','t12',)

def get_random(value):
    return value and random.choice(range(value)) or 0


def rounded(value):
    if isinstance(value, numbers.Number):
        return isinstance(value, float) and round(value, DEFAULT_DOC09_DIGITS) or isinstance(value, int) and value or 0
    return value


def getvalue(ob, key):
    return ob and hasattr(ob, key) and getattr(ob, key) or 0


def getRegionTitle(region):
    return region is not None and isinstance(region, Region) and region.name or ''


#   -----------------

class Base:
    
    def __init__(self):
        if IsDeepDebug:
            print('Doc09 Base init')

        self.pregion = ''

    @property
    def cols(self):
        return ['pregion']

    def generate(self):
        pass


class Plan(Base):
    
    def __init__(self):
        if IsDeepDebug:
            print('Doc09 Plan init')

        super().__init__()

        self.ptotal = 0
        self.c1 = 0
        self.c2 = 0
        self.c3 = 0

    @property
    def cols(self):
        return super().cols + ['ptotal','c1','c2','c3']

    def generate(self, max_value):
        self.c1 = get_random(max_value)
        self.c2 = get_random(max_value)
        self.c3 = get_random(max_value)

        self.ptotal = self.c1 + self.c2 + self.c3


class Fact(Base):
    
    def __init__(self, is_region=0):
        if IsDeepDebug:
            print('Doc09 Fact init')

        super().__init__()

        self.ftotal = 0
        self.t11 = 0.0
        self.t12 = ''
        self.g10 = ''
        self.c11 = 0
        self.c12 = 0
        self.c13 = 0
        self.t111 = 0.0
        self.t121 = 0.0
        self.t131 = 0.0
        
        self.is_region = is_region

    @property
    def cols(self):
        return ['ftotal','t11',] + (not self.is_region and ['t12',] or []) + ['c11','t111','c12','t121','c13','t131']

    def set_status(self):
        self.t11 = 0.0
        self.t12 = ''

        if self.ptotal and self.ftotal:
            self.t11 = rounded((self.ftotal / self.ptotal) * 100)
            if not self.is_region:
                self.t12 = self.ftotal < self.ptotal and 'down' or 'up'

    def set_total(self):
        self.ptotal = self.c1 + self.c2 + self.c3
        self.ftotal = self.c11 + self.c12 + self.c13

        if self.c1 > 0:
            self.t111 = round((self.c11 / self.c1) * 100, 2)
        if self.c2 > 0:
            self.t121 = round((self.c12 / self.c2) * 100, 2)
        if self.c3 > 0:
            self.t131 = round((self.c13 / self.c3) * 100, 2)

        self.set_status()

    def generate(self, plan):
        k = 10*get_random(2)
        self.c1 = plan.c1
        self.c11 = get_random(self.c1+k)

        self.c2 = plan.c2
        self.c12 = get_random(self.c2+k)

        self.c3 = plan.c3
        self.c13 = get_random(self.c3+k)

        self.set_total()


class Doc09Item:
    
    def __init__(self, is_region=0):
        if IsDeepDebug:
            print('Doc09Item init')

        self.region = None
        self.pregion = ''
        self.pindex = 0
        self.css = ''

        self.is_region = is_region

        self.plan = Plan()
        self.fact = Fact(is_region=is_region)

    @property
    def cols(self):
        return self.plan.cols + self.fact.cols

    def _initstate(self, force=None):
        for col in self.plan.cols:
            if col in DEFAULT_DOC09_COLS_EXCLUDE:
                continue
            val = getvalue(self.plan, col)
            setattr(self, col, val)
            if force:
                setattr(self.fact, col, val)

        for col in self.fact.cols:
            val = getvalue(self.fact, col)
            setattr(self, col, val)

    def _setstate(self, region=None, title=None, **kw):
        if not title:
            title = getRegionTitle(region)

        self.pregion = title

        css =''

        if region is not None:
            self.pindex = region.index
            css = 'region_level%s' % region.level
        else:
            css = 'top'
        
        self.css = css

        self.region = region

    def generate(self, region=None, specialities=None):
        self.plan.generate(10)
        self.fact.generate(self.plan)

        self._initstate()
        self._setstate(region=region)


class Doc09:

    def __init__(self, count=0, is_region=0):
        self.count = count or DEFAULT_DOC09_ROWS_COUNT
        self.rows = []
        self.cols = []
        
        self.is_region = is_region

    def set_cols(self):
        self.cols = Doc09Item().cols

    def set_total(self, title, **kw):
        row_total = Doc09Item()

        level = kw.get('level', 0)
        uid = kw.get('uid')

        value = None
        
        self.set_cols()

        for col in self.cols:
            if col in DEFAULT_DOC09_COLS_EXCLUDE + DEFAULT_DOC09_COLS_TOTAL:
                continue
            value = 0
            for row in self.rows:
                region = row.region
                if not region:
                    continue
                if uid and not region.uid.startswith(uid) or level > -1 and region.level != level:
                    continue
                x = getvalue(row, col)
                if isinstance(x, numbers.Number):
                    value += x
            value = rounded(value)
            setattr(row_total, col, value)
            if col in row_total.plan.cols:
                setattr(row_total.plan, col, value)
            elif col in row_total.fact.cols:
                setattr(row_total.fact, col, value)

        row_total._initstate(force=1)
        row_total.fact.set_total()

        for col in DEFAULT_DOC09_COLS_TOTAL + DEFAULT_DOC09_COLS_STATUS:
            setattr(row_total, col, getvalue(row_total.fact, col))

        row_total._setstate(title=title, **kw)
        
        return row_total

    def generate(self, data, regions, region_index, speciality_index):
        current_level = 0
        for index in region_index:
            if len(self.rows) == self.count:
                break
            region = regions.get_by_index(int(index))
            if not region:
                continue

            if not current_level:
                current_level = region.level
            if region.level == current_level - 1:
                row = self.set_total(region.name, uid=region.uid, level=current_level, region=region)
            else:
                row = Doc09Item(is_region=self.is_region)
                row.generate(region=region, specialities=speciality_index)

            self.rows.append(row)

        self.rows.sort(key=lambda x: x.region and x.region.uid or '0')
        #self.rows.sort(key=lambda x: int(x.pindex))

        if not self.is_region:
            row_total = self.set_total(maketext('All Russia'), uid='0', level=1)

            self.rows.insert(0, row_total)
            self.rows.append(row_total)
        
def get_specialities(specialities, speciality_index):
    values = []
    spc = maketext('SPC')
    for index in speciality_index:
        ob = specialities.get_by_index(int(index))
        value = '%s-%s' % (spc, ob.number)
        values.append(value)
    return ', '.join(values)


def get_regions(regions):
    region_index = get_request_item('region_index', is_iterable=True, delimeter=':', splitter='/') or []
    region_items = [region for region in regions.items if region.index in region_index]
    items = sorted(region_items, key=lambda x: x.uid, reverse=True)
    indexes = [x.index for x in items]
    return indexes
    

def render(mode, **kw):
    if mode != 'doc09':
        return {}

    args = kw.get('args')

    data = get_data(f'{mode}.json')
    period = args.get('period')

    regions = kw.get('regions')
    region_index = get_regions(regions)

    specialities = kw.get('specialities')
    speciality_index = get_request_item('speciality_index', is_iterable=True, delimeter=':', splitter='/') or []
    specialities_title = get_specialities(specialities, speciality_index)

    doc = Doc09(count=len(region_index))
    
    doc.generate(data, regions, region_index, speciality_index)

    # Формат листа печати
    orientation = 'landscape'

    return {
        'orientation' : orientation,
        'specialities_title' : specialities_title,
        'rows' : doc.rows,
        'cols' : doc.cols,
    }
