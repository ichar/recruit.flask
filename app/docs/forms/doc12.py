# -*- coding: utf-8 -*-


from app.settings import get_request_item

from . import get_data
from .doc11 import Doc11, get_specialities, get_regions, get_report_year


#   -------------------------------------------------------------------------
#   Сведения о ходе подготовки граждан по специальности (ВУС) в отчетном году
#   -------------------------------------------------------------------------


def render(mode, **kw):
    if mode != 'doc12':
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

    title_end = len(speciality_index) > 1 and 'ям' or 'и'

    doc = Doc11(count=len(region_index), is_speciality=1)
    
    doc.generate(data, regions, region_index, speciality_index)

    # Формат листа печати
    orientation = 'landscape'

    return {
        'orientation' : orientation,
        'specialities_title' : specialities_title,
        'title_end' : title_end,
        'report_year' : report_year,
        'rows' : doc.rows,
        'cols' : doc.cols,
    }
