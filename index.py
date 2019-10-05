#!/usr/bin/env python

import os
from glob import glob
import cgi, cgitb
import config as cfg


def get_uids():
    ready_uids = []
    dirs = glob(os.path.join(cfg.wip_path,'*',''))
    for d in dirs:
         uid = cfg.get_uid_from_dir(d)
         if uid:
              ready_uids.append(uid)
    return ready_uids

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

    for uid in get_uids():
        print '''
         <div class="grid-item">'''
        print ''' <a href="promote.py?uid=%s"> %s </a> ''' % (uid, uid)
        print '''</div>'''

    print '''
     </div>
    </body>
    </html>'''


if __name__ == '__main__':
    present()
