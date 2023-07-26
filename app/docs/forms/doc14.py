# -*- coding: utf-8 -*-

__all__ = ['render', 'get_specialities', 'Doc14']

import random
import numbers

from app.settings import get_request_item, maketext
from app.utils import getToday, getDate, getUserShortName

from config import IsDeepDebug

from . import get_data, today, Region, default_date_format


#   ------------------------------------------------------------------------------------------------------------
#   Сведения об обеспеченности образовательных организаций и учебных пунктов материально-техническими средствами
#   ------------------------------------------------------------------------------------------------------------


DEFAULT_DOC14_ROWS_COUNT = 10
DEFAULT_DOC14_ITEMS = 4
DEFAULT_DOC14_TOTAL = 3
DEFAULT_DOC14_DIGITS = 2
DEFAULT_DOC14_COLS_EXCLUDE = ('pregion', 'css',)
DEFAULT_DOC14_COLS_TOTAL = ()
DEFAULT_DOC14_COLS_STATUS = ()

def get_random(value):
    return value and random.choice(range(value)) or 0


def rounded(value):
    if isinstance(value, numbers.Number):
        return isinstance(value, float) and round(value, DEFAULT_DOC14_DIGITS) or isinstance(value, int) and value or 0
    return value


def getvalue(ob, key):
    return ob and hasattr(ob, key) and getattr(ob, key) or 0


def getRegionTitle(region):
    return region is not None and isinstance(region, Region) and region.name or ''


#   -----------------

class Base:
    
    def __init__(self):
        if IsDeepDebug:
            print('Doc14 Base init')

        self.pregion = ''

    @property
    def cols(self):
        return ['pregion']

    def generate(self):
        pass


class Plan(Base):
    
    def __init__(self):
        if IsDeepDebug:
            print('Doc14 Plan init')

        super().__init__()

        self.p1 = 0
        self.p2 = 0
        self.p3 = 0
        self.p4 = 0

    @property
    def cols(self):
        return super().cols + ['p1','p2','p3','p4']

    def generate(self, max_value):
        self.p1 = max_value + ((get_random(1) and -1 or 1) * get_random(10))
        self.p2 = max_value + ((get_random(1) and -1 or 1) * get_random(10))
        self.p3 = max_value + ((get_random(1) and -1 or 1) * get_random(10))
        self.p4 = max_value + ((get_random(1) and -1 or 1) * get_random(10))


class Fact(Base):
    
    def __init__(self, is_region=0, is_speciality=0):
        if IsDeepDebug:
            print('Doc14 Fact init')

        super().__init__()

        self.f1 = 0
        self.f2 = 0
        self.f3 = 0
        self.f4 = 0

        self.is_region = is_region
        self.is_speciality = is_speciality

    @property
    def cols(self):
        return ['f1','f2','f3','f4','c1','c2','c3','c4']

    def set_status(self):
        pass

    def set_total(self, plan=None):

        self.set_status()

    def generate(self, plan):
        k = 10*get_random(2)
        for col in self.cols:
            if col.startswith('f'):
                setattr(self, col, get_random(k))

        self.set_total(plan)


class Doc14Item:
    
    def __init__(self, is_region=0, is_speciality=0):
        if IsDeepDebug:
            print('Doc14Item init')

        self.region = None
        self.pregion = ''
        self.pindex = 0
        self.css = ''

        self.c1 = 0
        self.c2 = 0
        self.c3 = 0
        self.c4 = 0

        self.is_region = is_region
        self.is_speciality = is_speciality

        self.plan = Plan()
        self.fact = Fact(is_region=is_region, is_speciality=is_speciality)

    @property
    def cols(self):
        return [
            # Регион
            'pregion',
            # -------------------------------------------------------------
            # Обеспеченность общевойсковыми приборами радиационной разведки
            # -------------------------------------------------------------
            # положено
            'p1',
            # имеется
            'f1',
            # %
            'c1',
            # -----------------------------------------------------------
            # Обеспеченность общевойсковыми приборами химической разведки
            # -----------------------------------------------------------
            # положено
            'p2',
            # имеется
            'f2',
            # %
            'c1',
            # ------------------------------------
            # Обеспеченность защитными комплектами
            # ------------------------------------
            # положено
            'p3',
            # имеется
            'f3',
            # %
            'c3',
            # ----------------------------
            # Обеспеченность противогазами
            # ----------------------------
            # положено
            'p4',
            # имеется
            'f4',
            # %
            'c4',
            ]

    def _initstate(self, force=None):
        for col in self.plan.cols:
            val = getvalue(self.plan, col)
            setattr(self, col, val)

        for col in self.fact.cols:
            val = getvalue(self.fact, col)
            setattr(self, col, val)

        self.c1 = self.p1 and rounded((self.f1 / self.p1) * 100) or 0
        self.c2 = self.p2 and rounded((self.f2 / self.p2) * 100) or 0
        self.c3 = self.p3 and rounded((self.f3 / self.p3) * 100) or 0
        self.c4 = self.p4 and rounded((self.f4 / self.p4) * 100) or 0

    def _setstate(self, region=None, title=None, **kw):
        if not title:
            title = getRegionTitle(region)

        setattr(self, 'pregion', title)

        css =''

        if region is not None:
            self.pindex = region.index
            css = 'region_level%s' % region.level
        else:
            css = 'top'
        
        setattr(self, 'css', css)

        self.region = region
                    
    def generate(self, region=None, specialities=None):
        self.plan.generate(10)
        self.fact.generate(self.plan)

        self._initstate()
        self._setstate(region=region)


class Doc14:

    def __init__(self, count=0, is_region=0, is_speciality=0):
        self.count = count or DEFAULT_DOC14_ROWS_COUNT
        self.rows = []
        self.cols = []
        
        self.is_region = is_region
        self.is_speciality = is_speciality

    def set_cols(self):
        self.cols = Doc14Item().cols

    def set_total(self, title, **kw):
        row_total = Doc14Item()

        level = kw.get('level', 0)
        uid = kw.get('uid')

        value = None

        self.set_cols()

        for col in self.cols:
            if col in DEFAULT_DOC14_COLS_EXCLUDE + DEFAULT_DOC14_COLS_TOTAL:
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

        for col in DEFAULT_DOC14_COLS_TOTAL + DEFAULT_DOC14_COLS_STATUS:
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
                row = Doc14Item(is_region=self.is_region, is_speciality=self.is_speciality)
                row.generate(region=region, specialities=speciality_index)

            self.rows.append(row)

        self.rows.sort(key=lambda x: x.region and x.region.uid or '0')

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


def get_report_year():
    date = getDate(get_request_item('date_to'), format=default_date_format, is_date=True)
    if not date:
        date = today()
    return getDate(getDate(date, format=default_date_format, is_date=True), format='%Y')


def render(mode, **kw):
    if mode != 'doc14':
        return {}

    args = kw.get('args')

    data = get_data(f'{mode}.json')
    period = args.get('period')

    report_year = get_report_year()

    regions = kw.get('regions')
    region_index = get_regions(regions)

    specialities = kw.get('specialities')
    speciality_index = get_request_item('speciality_index', is_iterable=True, delimeter=':', splitter='/') or []
    specialities_title = get_specialities(specialities, speciality_index)

    doc = Doc14(count=len(region_index))
    
    doc.generate(data, regions, region_index, speciality_index)

    # Формат листа печати
    orientation = 'landscape'

    return {
        'orientation' : orientation,
        'specialities_title' : specialities_title,
        'report_year' : report_year,
        'rows' : doc.rows,
        'cols' : doc.cols,
    }
