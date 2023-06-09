# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: Copyright contributors to the OpenScanHub project.

"""
    TODO Once on 1.5, use filter from django.contrib.humanize
"""

import json
from collections import OrderedDict

from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse

from osh.hub.scan.models import SystemRelease
from osh.hub.stats.models import StatResults, StatType
from osh.hub.stats.service import display_values


def release_list(request, release_id):
    context = {}
    context['release'] = SystemRelease.objects.get(id=release_id)

    context['results'] = OrderedDict()
    for stattype in StatType.objects.filter(is_release_specific=True).\
            order_by('group', 'order'):
        context['results'][stattype] = stattype.display_value(
            context['release']), stattype.detail_url(context['release'])

    return render(request, "stats/list.html", context)


def stats_list(request):
    context = {}
    int_releases = StatResults.objects.all().values_list(
        'release__id', flat=True).distinct()
    context['releases'] = SystemRelease.objects.filter(id__in=int_releases)

    context['results'] = OrderedDict()
    for stattype in StatType.objects.filter(is_release_specific=False).\
            order_by('group', 'order'):
        context['results'][stattype] = stattype.display_value(), \
            stattype.detail_url()

    return render(request, "stats/list.html", context)


def release_stats_detail(request, release_id, stat_id):
    context = {}
    context['release'] = SystemRelease.objects.get(id=release_id)
    context['type'] = StatType.objects.get(id=stat_id)
    context['results'] = display_values(context['type'], context['release'])
    context['json_url'] = reverse('stats/release/detail/graph',
                                  args=[stat_id, release_id])

    return render(request, "stats/detail.html", context)


def stats_detail(request, stat_id):
    context = {}
    context['type'] = StatType.objects.get(id=stat_id)
    context['results'] = display_values(context['type'])
    context['json_url'] = reverse('stats/detail/graph', args=[stat_id])
    return render(request, "stats/detail.html", context)


def stats_detail_graph(request, stat_id, release_id=None):
    """
    Provide data for graph.
    """
    if release_id is not None:
        release = SystemRelease.objects.get(id=release_id)
        label = release.tag
        sr = StatResults.objects.filter(stat=stat_id, release=release)
    else:
        label = 'Global'
        sr = StatResults.objects.filter(stat=stat_id)

    st = StatType.objects.get(id=stat_id)

    data = {
        'title': st.short_comment,
        'subtitle': st.comment,
        'label': label,
        'x': [],
        'y': [],
    }

    for result in sr.order_by('-date')[:12]:
        data['x'].append(result.date.strftime("%Y-%m-%d"))
        data['y'].append(result.value)

    return HttpResponse(json.dumps(data).encode(),
                        content_type='application/json; charset=utf8')
