# -*- coding: utf-8 -*-

__all__ = ['render', 'get_specialities', 'Doc13']

import random
import numbers

from app.settings import get_request_item, maketext
from app.utils import getToday, getDate, getUserShortName

from config import IsDeepDebug

from . import get_data, today, Region, default_date_format


#   --------------------------------------------------------------------------------------------------------------------------------
#   Сведения о количестве граждан, охваченных подготовкой по основам военной службы в образовательных организациях и учебных пунктах
#   --------------------------------------------------------------------------------------------------------------------------------


DEFAULT_DOC13_ROWS_COUNT = 10
DEFAULT_DOC13_ITEMS = 4
DEFAULT_DOC13_TOTAL = 3
DEFAULT_DOC13_DIGITS = 2
DEFAULT_DOC13_COLS_EXCLUDE = ('pregion', 'css',)
DEFAULT_DOC13_COLS_TOTAL = ()
DEFAULT_DOC13_COLS_STATUS = ()

def get_random(value):
    return value and random.choice(range(value)) or 0


def rounded(value):
    if isinstance(value, numbers.Number):
        return isinstance(value, float) and round(value, DEFAULT_DOC13_DIGITS) or isinstance(value, int) and value or 0
    return value


def getvalue(ob, key):
    return ob and hasattr(ob, key) and getattr(ob, key) or 0


def getRegionTitle(region):
    return region is not None and isinstance(region, Region) and region.name or ''


#   -----------------

class Base:
    
    def __init__(self):
        if IsDeepDebug:
            print('Doc13 Base init')

        self.pregion = ''

    @property
    def cols(self):
        return ['pregion']

    def generate(self):
        pass


class Plan(Base):
    
    def __init__(self):
        if IsDeepDebug:
            print('Doc13 Plan init')

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
            print('Doc13 Fact init')

        super().__init__()

        self.fvalue = 0
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

        self.is_region = is_region
        self.is_speciality = is_speciality

    @property
    def cols(self):
        attrs = [key for key, value in self.__dict__.items() if not key.startswith("__") and (key.startswith('p') or key.startswith('f'))]
        return attrs

    def set_status(self):
        pass

    def set_total(self, plan=None):
        self.fvalue = self.p2 + self.p4 + self.p6 + self.p8
        self.p1 = self.p3 + self.p5 + self.p7 + self.p9
        self.p9 = get_random(self.p8)

        if plan is not None:
            plan.generate(self.fvalue)

        self.set_status()

    def generate(self, plan):
        k = 10*get_random(2)
        for col in self.cols:
            setattr(self, col, get_random(k))

        self.set_total(plan)


class Doc13Item:
    
    def __init__(self, is_region=0, is_speciality=0):
        if IsDeepDebug:
            print('Doc13Item init')

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
            # количество граждан, подлежащих постановке на воинский учет в прошедшем учебном году
            'pvalue',
            # всего
            'fvalue',
            # из них прошли учебные сборы
            'p1',
            # ------------------------------
            # в образовательных организациях
            # ------------------------------
            # всего
            'p2',
            # из них прошли учебные сборы
            'p3',
            # ----------------------------------------------------------
            # в образовательных организациях среднего общего образования
            # ----------------------------------------------------------
            # всего
            'p4',
            # из них прошли учебные сборы
            'p5',
            # ---------------------------------------------------------------------
            # в образовательных организациях среднего профессионального образования
            # ---------------------------------------------------------------------
            # всего
            'p6',
            # из них прошли учебные сборы
            'p7',
            # ---------
            # в учебных
            # ---------
            # всего
            'p8',
            # из них прошли учебные сборы
            'p9',
            # прошли подготовку к военной службе в оборонно-спортивных оздоровительных лагерях
            'p10',
            # обучаются в военно-патриотических молодежных объединениях
            'p11',
            # занимаются военно-прикладными видами спорта
            'p12',
            ]
        return ('pregion','pvalue','fvalue','p1','p10','p11','p12','p2','p3','p8','p9','p4','p5','p6','p7')

    def _initstate(self, force=None):
        for col in self.plan.cols:
            if col in DEFAULT_DOC13_COLS_EXCLUDE:
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


class Doc13:

    def __init__(self, count=0, is_region=0, is_speciality=0):
        self.count = count or DEFAULT_DOC13_ROWS_COUNT
        self.rows = []
        self.cols = []
        
        self.is_region = is_region
        self.is_speciality = is_speciality

    def set_cols(self):
        self.cols = Doc13Item().cols

    def set_total(self, title, **kw):
        row_total = Doc13Item()

        level = kw.get('level', 0)
        uid = kw.get('uid')

        value = None

        self.set_cols()

        for col in self.cols:
            if col in DEFAULT_DOC13_COLS_EXCLUDE + DEFAULT_DOC13_COLS_TOTAL:
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

        for col in DEFAULT_DOC13_COLS_TOTAL + DEFAULT_DOC13_COLS_STATUS:
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
                row = Doc13Item(is_region=self.is_region, is_speciality=self.is_speciality)
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
    if mode != 'doc13':
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

    doc = Doc13(count=len(region_index))
    
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
