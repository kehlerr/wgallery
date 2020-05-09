#!/usr/bin/env python

import os
from glob import glob
import json
import cgi, cgitb
import config as cfg


def get_ponds():
    ponds = []
    with open(cfg.get_ponds_db(), 'r') as fp:
        db_json = json.load(fp)
        for v in db_json['ponds']:
            ponds.append(db_json['ponds'][v])
    return ponds

def present():
    print "Content-type:text/html\r\n\r\n"
    print '''
<html>
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <title>Welcome, master</title>
    <link rel="stylesheet" type="text/css" href="css/common.css"/>
</head>

<body>
    <div class="grid-container">
'''

    for p in get_ponds():
        print '''
        <div class="grid-item">
            <a href="promote.py?uid=%s">
                <div style="background-color:#b9ffdb;font-size:26;margin-bottom: 5px;margin-right: 7;border-radius: 7px;padding: 5px;padding-left: 10px;">
             %s</div> </a>''' % (p['uid'], p['uid'])
        create_count_info(p['overall_count'], p['promo_count'], p['todel_count'])
        print '''</div>'''

    print '''
     </div>
    </body>
    </html>'''


def create_count_info(t, p, d):
    print ''' <div>
    <a style="text-decoration-color:darkslategrey"
    href=promote.py?uid=%s>''' % "self.uid"
    print '''<span style="color:darkslategrey">%d</span></a></b>''' % t

    if p > 0:
        print '''<a style="text-decoration-color:green"
        href=promote.py?uid=%s&srcl=promo>''' % "self.uid"
        print ''' <span style="color:green">/<b>%d</b></span></a>''' % p

    if d > 0:
        print '''<a style="text-decoration-color:#e01632"
        href=promote.py?uid=%s&srcl=todel>''' % "self.uid"
        print '''<span style="color:#e01632">/<b>%d</b></span></a>''' % d

    print ''' </div> '''

if __name__ == '__main__':
    present()
