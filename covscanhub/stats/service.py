# -*- coding: utf-8 -*-


import stattypes
import types
from models import StatType, StatResults
from covscanhub.scan.models import SystemRelease

def get_mapping():
    mapping = {}
    for binding_name in dir(stattypes):
        binding = getattr(stattypes, binding_name)
        if isinstance(binding, types.FunctionType) and\
                binding.__name__.startswith('get_'):
            mapping[binding] = (binding.__name__[4:].upper(),
                                binding.__doc__.strip())
    return mapping


def create_stat_result(key, comment, value, release_tag=None):
    s = StatResults()
    st, created = StatType.objects.get_or_create(key=key,
                                                 comment=comment)
    s.stat = st

    s.value = value
    if release_tag is not None:
        s.release = SystemRelease.objects.get(tag=release_tag)
    s.save()



def update():
    """
    Update statistics data.
    """
    for func, desc in get_mapping().iteritems():
        stat_data = func()
        if isinstance(stat_data, int):
            create_stat_result(desc[0], desc[1], stat_data)
        elif isinstance(stat_data, dict):
            for s in stat_data:
                create_stat_result(desc[0], desc[1], stat_data[s], s)


def display_values_inline(stat_type):
    results = StatResults.objects.filter(stat=stat_type)
    response = ''    
    if 'RELEASE' in stat_type.key:
        for s in SystemRelease.objects.all()
            response += "%s = %s, " % (
                s.tag,
                result.filter(release=s).latest().value,
            )
    else:
        response = results.latest()
    if len(response) > 50:
        return mark_safe(response[:50] + '...')
    else:
        return mark_safe(response[:len(response) - 2])


def display_values(stat_type):
    results = StatResults.objects.filter(stat=stat_type)
    response = ''    
    if 'RELEASE' in stat_type.key:
        for s in SystemRelease.objects.all()
            response += "<b>%s</b> = %s<br/ >\n" % (
                s.tag,
                result.filter(release=s).latest().value,
            )
    else:
        response = results.latest()
    return mark_safe(response)