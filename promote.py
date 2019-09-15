#!/usr/bin/env python

import os.path

# Import modules for CGI handling 
import cgi, cgitb 

cgitb.enable()

import config as cfg
import index

def get_path_url_file(uid):
    return cfg.wip_path + str(uid) + cfg.list_file_ext

def get_path_saved_urls_file(uid):
    return cfg.wip_path + str(uid) + cfg.saved_urls_file_suffix + cfg.saved_urls_file_ext

class Page:
    def __init__(self, form_data):
        self.uid = form_data['url_id']
        self.offset = form_data['offset']
        self.checked_data = form_data['checkd'] 
        self.checked_list = []
        self.fill_checked_list()
        self.process_checked()

        self.urls_list = []
        self.fill_urls_list()
        self.urls_amount = len(self.urls_list)


    def fill_urls_list(self):
        filename = get_path_url_file(self.uid)
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                self.urls_list = f.read().split('\n')

    def fill_checked_list(self):
        path_saved_file = get_path_saved_urls_file(self.uid)
        with open(path_saved_file, 'r') as f:
            self.checked_list = f.read().split('\n')

    def present(self):
        if self.uid == 0:
            index_page.present()
        else:
            self.present_heads()
            self.present_body()

    def present_heads(self):
        print "Content-type:text/html\r\n\r\n"
        print '''<html>
                 <head>
                     <title>Likee - save videos!</title>
                 </head>'''

    def present_body(self):
        print "<body>"
        self.create_main_form()
        self.create_navigations_refs()
        print "</body>"
        print "</html>"

    def create_main_form(self):
        print '''<form action="/cgi-enabled/promote.py" method="POST">'''

        self.create_videos()

        print '''   <input style="background-color:powderblue; height:100px; width:300px;margin-left:0px;margin-top:0px;" type="submit" value="Submit">'''
        print '''   <input type="hidden" name="offset" value="%s">''' % str(self.offset + cfg.videos_on_page)
        print '''   <input type="hidden" name="uid" value="%s">''' % self.uid
        print ''' </form> ''' 

    def create_videos(self):
        for i in range(1, cfg.videos_on_page):
            self.create_video_field(i, self.offset + i)

    def create_video_field(self, idx, vid_num):
        url = self.get_url_by_number(vid_num)
        background_color = self.is_video_checked(url) and '#4aff68' or '#c8c8fd'
        print(url)
        print '''<div style="background-color:%s;position:relative;max-width:255px;border:2px solid;">''' % (background_color)
        print '''   <video width="200" height="350" controls="">'''
        print '''       <source src="%s" type="video/mp4"> ''' % url
        print '''   </video>    '''
        print '''   <input style="height:50px;width:50px;margin-left:200px;margin-top:-200px;" type="checkbox" name="vid_num_%s" value="%s"> ''' % (str(idx), url)
        print '''</div>'''
    
    def get_url_by_number(self, n):
        number_in_list = n > 0 and n < self.urls_amount
        return number_in_list and self.urls_list[n-1] or ''

    def create_navigations_refs(self):
        print ''' <table> '''
        print ''' <tbody> '''
        print ''' <tr valign="top"> '''

        refs_count = self.urls_amount / cfg.videos_on_page + 1
        for i in range(refs_count):
            self.create_ref_button(i)

        print ''' </tr> '''
        print ''' </tbody> '''
        print ''' </table> '''


    def create_ref_button(self,idx):
        print '''<td style="width:35px">'''
        offset_number = idx*cfg.videos_on_page
        offset_str = str(offset_number)
        if offset_number != self.offset:
            href = "/cgi-enabled/promote.py" + '?offset=' + offset_str + '&uid='+self.uid
            print '''<a aria-label="%s" href="%s">''' %(offset_str, href)
            print offset_str
            print "</a>"
        else:
            print offset_str
        print "</td>"


    def process_checked(self):
        if len(self.checked_data) > 0:
            for url in self.checked_data:
                if not self.is_video_checked(url):
                    self.checked_list.append(url)
                else:
                    self.checked_list.remove(url)
            self.write_checked()
        self.checked_data = None
          
    def write_checked(self):
        path_saved_file = get_path_saved_urls_file(self.uid)
        with open(path_saved_file, 'w+') as f:
            for url in self.checked_list:
                f.write(url + '\n')

    def is_video_checked(self,url):
        return url in self.checked_list    


def get_form_data():
    data={}

# Create instance of FieldStorage 
    form = cgi.FieldStorage() 

# Get data from fields
    value_offset = form.getvalue('offset')
    data['offset'] = value_offset and int(value_offset) or 0
    data['url_id'] = form.getvalue('uid') or 0
    data['checkd'] = []

    for i in range(1, cfg.videos_on_page):
        val = form.getvalue('vid_num_'+str(i))
        if val:
            data['checkd'].append(val)

    return data

if __name__ == '__main__':
    form_data = get_form_data()
    current_page = Page(form_data)
    current_page.present()
