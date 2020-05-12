#!/usr/bin/env python

import os
from glob import glob
import json
import cgi, cgitb
import config as cfg


def get_ponds(pond_type):
    ponds = []
    with open(cfg.get_ponds_db(), 'r') as fp:
        db_json = json.load(fp)
        for v in db_json['ponds']:
            pond = db_json['ponds'][v]
            if not pond_type or pond_type == pond['type']:
                ponds.append(pond)

    sort_ponds = sorted(ponds, key=lambda i: i['overall_count'])
    return sort_ponds

def present(form_data):
    print "Content-type:text/html\r\n\r\n"
    print '''
<html>
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <title>Welcome, master</title>
    <link rel="stylesheet" type="text/css" href="css/common.css"/>
</head>

<body>
    <div style="background-color:#b5e270;font-size: larger;margin-bottom: 5px;margin-right: 7;border-radius: 7px;padding: 5px;padding-left: 10px;">
        <a style="text-decoration-color:darkslategrey" href="index.py">
            <span style="color:darkslategrey"><b>Common</b></span>
        </a>
        <a style="text-decoration-color:darkviolet" href="index.py?type=profile">
            <span style="color: darkviolet;">/Profiles</span>
        </a>
        <a style="text-decoration-color:dodgerblue" href="index.py?type=sound">
            <span style="color: dodgerblue;">/Sounds</span>
        </a>
        <a style="text-decoration-color:forestgreen" href="index.py?type=custom">
            <span style="color:forestgreen">/Custom</span>
        </a>
    </div>
    <div class="grid-container">
'''

    for p in get_ponds(form_data['ponds_type']):
        print '''
        <div class="grid-item">
            <a href="promote.py?uid=%s">
                <div style="background-color:#b9ffdb;font-size:26;margin-bottom: 5px;margin-right: 7;border-radius: 7px;padding: 5px;padding-left: 10px;">
             %s</div> </a>''' % (p['uid'], p['uid'])
        create_count_info(p['uid'], p['overall_count'], p['promo_count'], p['todel_count'])
        print '''</div>'''

    print '''
     </div>
    </body>
    </html>'''


def create_count_info(uid, t, p, d):
    print ''' <div>
    <a style="text-decoration-color:darkslategrey"
    href=promote.py?uid=%s>''' % uid
    print '''<span style="color:darkslategrey">%d</span></a></b>''' % t

    if p > 0:
        print '''<a style="text-decoration-color:green"
        href=promote.py?uid=%s&srcl=promo>''' % uid
        print ''' <span style="color:green">/<b>%d</b></span></a>''' % p

    if d > 0:
        print '''<a style="text-decoration-color:#e01632"
        href=promote.py?uid=%s&srcl=todel>''' % uid
        print '''<span style="color:#e01632">/<b>%d</b></span></a>''' % d

    print ''' </div> '''

if __name__ == '__main__':
    form = cgi.FieldStorage()
    form_data = {
        'ponds_type':form.getvalue('type')
    }

    present(form_data)
