# -*- coding: utf-8 -*-


from app.settings import get_request_item

from . import get_data
from .doc09 import Doc09, get_specialities, get_regions


#   ------------------------------------------------------------------
#   Сведения о  ходе отправки граждан, подготовленных по ВУС (Регионы)
#   ------------------------------------------------------------------


def render(mode, **kw):
    if mode != 'doc10':
        return {}

    args = kw.get('args')

    data = get_data(f'{mode}.json')
    period = args.get('period')

    regions = kw.get('regions')
    region_index = get_regions(regions)

    specialities = kw.get('specialities')
    speciality_index = get_request_item('speciality_index', is_iterable=True, delimeter=':', splitter='/') or []
    specialities_title = get_specialities(specialities, speciality_index)

    doc = Doc09(count=len(regions.items), is_region=1)

    doc.generate(data, regions, region_index, speciality_index)

    # Формат листа печати
    orientation = 'landscape'

    return {
        'orientation' : orientation,
        'specialities_title' : specialities_title,
        'rows' : doc.rows,
        'cols' : doc.cols,
    }
