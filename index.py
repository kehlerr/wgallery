#!/usr/bin/env python

import os, re
import cgi, cgitb
import config as cfg

template_url_file = re.compile('[0-9]+'+cfg.list_file_ext)

def is_file_with_urls(filename):
    return template_url_file.match(filename)

def get_uids():
    workdir_content = os.listdir(cfg.wip_path)
    ready_uids = []
    for fname in workdir_content:
        if is_file_with_urls(fname):
            uid = fname.split(cfg.list_file_ext)[0]
            ready_uids.append(uid) 
    return ready_uids

def present():
    print "Content-type:text/html\r\n\r\n"
    print '''
<html>
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <title>Welcome, master</title>
</head>
<style>
body {
    background-position: center center;
    background-attachment: fixed;
    background-size: cover;
}
.sign {
    color: white;
    font-size: 200;
    font-family: Ubuntu;
    font-align: center;
    top: 250px;
}
.grid-container {
    display: grid;
    grid-template-columns: auto auto auto;
    background-color: #291a3e;
    padding: 10px;
    width: 98%;
}

.grid-item {
    background-color: rgba(213, 255, 255, 0.7);
    border: 1px solid rgba(0, 0, 0, 0.8);
    padding: 20px;
    font-size: 30px;
    text-align: center;
}
</style>

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
