# -*- coding: utf-8 -*-

__all__ = ['render', 'get_specialities', 'Doc11']

import random
import numbers

from app.settings import get_request_item, maketext
from app.utils import getToday, getDate, getUserShortName

from config import IsDeepDebug

from . import get_data, today, Region, default_date_format


#   -----------------------------------------------------------------------------------
#   Сведения о ходе подготовки граждан по военно-учетным специальностям в отчетном году
#   -----------------------------------------------------------------------------------


DEFAULT_DOC11_ROWS_COUNT = 10
DEFAULT_DOC11_ITEMS = 4
DEFAULT_DOC11_TOTAL = 3
DEFAULT_DOC11_DIGITS = 2
DEFAULT_DOC11_COLS_EXCLUDE = ('pregion', 'css',) #, 'pvalue'
DEFAULT_DOC11_COLS_TOTAL = () #('pvalue', 'fvalue',)
DEFAULT_DOC11_COLS_STATUS = ()

def get_random(value):
    return value and random.choice(range(value)) or 0


def rounded(value):
    if isinstance(value, numbers.Number):
        return isinstance(value, float) and round(value, DEFAULT_DOC11_DIGITS) or isinstance(value, int) and value or 0
    return value


def getvalue(ob, key):
    return ob and hasattr(ob, key) and getattr(ob, key) or 0


def getRegionTitle(region):
    return region is not None and isinstance(region, Region) and region.name or ''


#   -----------------

class Base:
    
    def __init__(self):
        if IsDeepDebug:
            print('Doc11 Base init')

        self.pregion = ''

    @property
    def cols(self):
        return ['pregion']

    def generate(self):
        pass


class Plan(Base):
    
    def __init__(self):
        if IsDeepDebug:
            print('Doc11 Plan init')

        super().__init__()

        self.pvalue = 0

    @property
    def cols(self):
        return super().cols + ['pvalue',]

    def generate(self, max_value):
        self.pvalue = max_value + ((get_random(1) and -1 or 1) * get_random(10))


class Fact(Base):
    
    def __init__(self, is_region=0, is_speciality=0):
        if IsDeepDebug:
            print('Doc11 Fact init')

        super().__init__()

        self.fvalue = 0
        self.f1 = 0
        self.c1 = 0
        self.c2 = 0
        self.c3 = 0
        self.c4 = 0
        self.c5 = 0
        self.p1 = 0
        self.p2 = 0
        self.p3 = 0
        self.p4 = 0
        self.p5 = 0
        self.p6 = 0
        self.p7 = 0
        self.p8 = 0
        self.p9 = 0
        self.p10 = 0
        self.p11 = 0
        self.p12 = 0
        self.p13 = 0
        self.p14 = 0
        self.p15 = 0
        self.p16 = 0
        self.p17 = 0
        self.p18 = 0
        self.p19 = 0
        self.p20 = 0
        self.p21 = 0
        self.p22 = 0
        self.p23 = 0
        self.p24 = 0

        self.is_region = is_region
        self.is_speciality = is_speciality

    @property
    def cols(self):
        attrs = [key for key, value in self.__dict__.items() if not key.startswith("__") and (key.startswith('p') or key.startswith('c') or key.startswith('f'))]
        return attrs

    def set_status(self):
        pass

    def set_total(self, plan=None):
        self.p1 = self.p5 + self.p16
        self.p2 = self.p6 + self.p17
        self.p5 = self.c1 - self.p6 - self.p7

        if plan is not None:
            plan.generate(self.p4 + self.p15)

        self.c1 = self.c1 - self.p6 - self.p7

        self.set_status()

    def generate(self, plan):
        k = 10*get_random(2)
        for col in self.cols:
            setattr(self, col, get_random(k))

        self.c1 += self.p6 + self.p7

        self.fvalue = get_random(k)

        self.set_total(plan)


class Doc11Item:
    
    def __init__(self, is_region=0, is_speciality=0):
        if IsDeepDebug:
            print('Doc11Item init')

        self.region = None
        self.pregion = ''
        self.pindex = 0
        self.css = ''

        self.is_region = is_region
        self.is_speciality = is_speciality

        self.plan = Plan()
        self.fact = Fact(is_region=is_region, is_speciality=is_speciality)

    @property
    def cols(self):
        columns = [
            # Регион
            'pregion',
            # Задание на подготовку
            'pvalue',
            # Направлено
            'p1',
            # Отчислено
            'p2',
            # ---------------
            # Весенний призыв
            # ---------------
            # Обучается всего
            'fvalue',
            # Обучается в том числе сдали ВЭК но не сдали ГИБДД
            'f1',
            # Подготовлено
            'p3',
            # задание на подготовку
            'p4',
            # направлено
            'p5',
            # отчислено
            'p6',
            # Обучается всего
            'c1',
            # Обучается в том числе сдали ВЭК но не сдали ГИБДД
            'c2',
            # подготовлено
            'p7',
            # задание на отправку
            'p8',
            # ДОСААФ России
            'p9',
            # СПО
            'p10',
            # Отправлено
            'p11',
            # ДОСААФ России
            'p12',
            # СПО
            'p13',
            # Другие организации
            'p14',
            # ---------------
            # Осенний призыв
            # ---------------
            # задание на подготовку
            'p15',
            # направлено
            'p16',
            # отчислено
            'p17',
            # всего
            'c3',
            # Обучается в том числе сдали ВЭК но не сдали ГИБДД
            'c4',
            # подготовлено
            'c5',
            # задание на отправку
            'p18',
            # ДОСААФ России
            'p19',
            # СПО
            'p20',
            # Отправлено
            'p21',
            # ДОСААФ России
            'p22',
            # СПО
            'p23',
            # Другие организации
            'p24',
            ]
        return ('pregion','ptotal','p1','p2','fvalue','f1','p3','p4','p5','p6','p7','p8','p11','p15','p16','p17','c5','p18','p21', \
                'c1','c2','p9','p10','p12','p13','p14','c3','c4','p19','p20','p22','p23','p24',)

    def _initstate(self, force=None):
        for col in self.plan.cols:
            if col in DEFAULT_DOC11_COLS_EXCLUDE:
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


class Doc11:

    def __init__(self, count=0, is_region=0, is_speciality=0):
        self.count = count or DEFAULT_DOC11_ROWS_COUNT
        self.rows = []
        self.cols = []
        
        self.is_region = is_region
        self.is_speciality = is_speciality

    def set_cols(self):
        self.cols = Doc11Item().cols

    def set_total(self, title, **kw):
        row_total = Doc11Item()

        level = kw.get('level', 0)
        uid = kw.get('uid')

        value = None

        self.set_cols()

        for col in self.cols:
            if col in DEFAULT_DOC11_COLS_EXCLUDE + DEFAULT_DOC11_COLS_TOTAL:
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

        for col in DEFAULT_DOC11_COLS_TOTAL + DEFAULT_DOC11_COLS_STATUS:
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
                row = Doc11Item(is_region=self.is_region, is_speciality=self.is_speciality)
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


def get_report_year():
    date = getDate(get_request_item('date_to'), format=default_date_format, is_date=True)
    if not date:
        date = today()
    return getDate(getDate(date, format=default_date_format, is_date=True), format='%Y')


def render(mode, **kw):
    if mode != 'doc11':
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

    doc = Doc11(count=len(region_index))
    
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
