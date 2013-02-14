# -*- coding: utf-8 -*-

from covscanhub.scan.messaging import post_qpid_message
from covscanhub.scan.models import SCAN_STATES

from kobo.django.xmlrpc.decorators import login_required

import random

__all__ = (
    'send_message',
)


@login_required
def send_message(request):
    """
    send_message()

    Posts message on qpid broker. It is generating random IDs and states.

    It is using currently this configuration:
        'broker': "qpid-stage.app.eng.bos.redhat.com"
        'address': "eso.topic"
        'mechanism': "GSSAPI"
        'routing_key': 'covscan.#'

    Message has this structure:
        {
            'scan_id': string, # random ID
            'scan_state': string, # random state
            'et_id': string, # random ID
        }
    """
    etm = True
    etm.id = random.randint(1, 10000)
    etm.et_scan_id = random.randint(1, 10000)
    scan_state = random.choice([value for (key, value)
                               in SCAN_STATES.get_mapping()])
    post_qpid_message(scan_state, etm,
                      random.choice(('unfinished', 'finished')))
    result = {
        'message': {
            'scan_id': str(etm.id),
            'scan_state': scan_state,
            'et_id': str(etm.et_scan_id),
        },
        'comment': 'The message provided has been sent to broker, for more \
info see documentation on \
http://uqtm.lab.eng.brq.redhat.com/covscan/xmlrpc/kerbauth/'
    }
    return result
