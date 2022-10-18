# -*- coding: utf-8 -*-

import os
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).parents[2]

if PROJECT_DIR not in sys.path:
    sys.path.append(PROJECT_DIR)

os.environ['DJANGO_SETTINGS_MODULE'] = 'covscanhub.settings'

from covscanhub.waiving.models import ResultGroup, Waiver, DEFECT_STATES

for rh in ResultGroup.objects.filter(defect_type=DEFECT_STATES['NEW']):
    wvrs = Waiver.objects.filter(result_group=rh, is_deleted=False)
    if wvrs:
        latest_waiver = wvrs.latest()
        latest_waiver.is_active = True
        latest_waiver.save()
