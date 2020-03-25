#!/usr/bin/env python

import os.path
import json

# Import modules for CGI handling 
import cgi, cgitb 

cgitb.enable()

import config as cfg
import index

class Page:
     def __init__(self, form_data):
          self.uid = form_data['url_id']
          self.offset = form_data['offset']
          self.checked_data = form_data['checkd'] 
          self.todelete_data = form_data['delete'] 
          self.checked_list = []
          self.fill_checked_list()
          self.process_checked()
          self.todelete_list = []
          self.fill_todelete_list()
          self.process_todelete()

          self.json_list = []
          self.fill_json_list()
          self.urls_amount = len(self.json_list)


     def fill_json_list(self):
          filename = cfg.get_path_json_urls_file(self.uid)
          if os.path.exists(filename):
               with open(filename, 'r') as f:
                    self.json_list = json.load(f)

     def fill_checked_list(self):
          path_saved_file = cfg.get_path_saved_urls_file(self.uid)
          if os.path.exists(path_saved_file):
               with open(path_saved_file, 'r') as f:
                    self.checked_list = f.read().split('\n')

     def fill_todelete_list(self):
          path_todelete_file = cfg.get_path_todelete_urls_file(self.uid)
          if os.path.exists(path_todelete_file):
               with open(path_todelete_file, 'r') as f:
                    self.todelete_list = f.read().split('\n')


     def present(self):
          if self.uid == 0:
               index.present()
          else:
               self.present_heads()
               self.present_body()

     def present_heads(self):
          print "Content-type:text/html\r\n\r\n"
          print '''<html>
                    <head>
                         <title>Likee - save videos!</title>
                         <link rel="stylesheet" type="text/css" href="css/common.css"/>
                    </head>'''

     def present_body(self):
          print '''<body>'''

          self.create_main_form()
          self.create_navigations_refs()
 
          print "</body>"
          print "</html>"

     def create_main_form(self):
          print '''<form action="/cgi-enabled/promote.py" method="POST">'''

          print '''<div class="grid-container">'''
          self.create_videos()
          print '''</div>'''
          print '''<div style="margin-left:515px;margin-top:15px;">         
                       <input class="enjoy-css" type="submit" value="Submit">
                         <script type="text/javascript" script-name="syncopate" src="http://use.edgefonts.net/syncopate.js"></script>'''
          print '''</div>'''
          print '''   <input type="hidden" name="offset" value="%s">''' % str(self.offset + cfg.videos_on_page)
          print '''   <input type="hidden" name="uid" value="%s">''' % self.uid
          print ''' </form> ''' 

     def create_videos(self):
          videos_on_page = min(cfg.videos_on_page, self.urls_amount - self.offset-1)
          for i in range(videos_on_page):
               self.create_video_field(i)

     def create_video_field(self, idx):
          vid_num = self.offset + idx+1
          post_data = self.get_data_by_number(vid_num)
          if not post_data:
               return
          url=post_data['videoUrl'].split('?')[0]
          poster_uid='posterUid' in post_data and post_data['posterUid'] or 0
          like_count='likeCount' in post_data and post_data['likeCount'] or 0
          comment_count='commentCount' in post_data and post_data['commentCount'] or 0
          background_color = '#c8c8fd'
          if self.is_video_checked(url):
               background_color = '#4aff68'
          elif self.is_video_todelete(url):
               background_color = '#ff7d7d'

          print '''<div class="grid-item">'''
          if poster_uid != 0:
               print '''<div style="font-size:0.6">%s</div>''' % (poster_uid)
          print '''   <div style="background-color:%s;border:2px solid;border-color:#00887b">''' % (background_color)
          print '''     <input style="height:35px;width:35px;margin:-10px;position:relative;left:0;top:-100" type="checkbox" name="del_vid_num_%s" value="%s"> ''' % (str(idx), url)
          print '''     <video width="220" height="360" controls="">'''
          print '''       <source src="%s" type="video/mp4"> ''' % url
          print '''     </video>    '''
          if poster_uid != 0:
               print ''' <div style="width:64px;font-size:0.6;float:right;margin-left:-80px;margin-right:12px;margin-top:40px;"> 
                         <img src="http://localhost/cgi-enabled/img/icon_like.png">
                         %s
                     </div>''' % like_count
               print ''' <div style="width:64px;font-size:0.6;float:right;margin-left:-40px;margin-right:12px;margin-top:120px;"> 
                         <img src="http://localhost/cgi-enabled/img/icon_comment.png">
                         %s
                    </div>''' % comment_count
          print '''   </div>'''
          print '''     <input style="height:50px;width:50px;margin:-20px;position:relative;left:150;top:-100" type="checkbox" name="vid_num_%s" value="%s"> ''' % (str(idx), url)
          print '''</div>'''

     def get_data_by_number(self, n):
          number_in_list = n > 0 and n < self.urls_amount
          return number_in_list and self.json_list[n-1]['data'][0] or None

     def create_navigations_refs(self):
          print ''' <table> <tbody> <tr valign="top"> '''

          current_page_idx = self.offset / cfg.videos_on_page + 1
          left_idx = max(0, current_page_idx - cfg.max_refs_count/2+1)
          refs_count = min(self.urls_amount / cfg.videos_on_page + 1 - left_idx, cfg.max_refs_count)
          for i in range(refs_count):
               self.create_ref_button(left_idx+i)

          print ''' </tr> </tbody> </table> '''


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
               #self.checked_data = None
          
     def write_checked(self):
          path_saved_file = cfg.get_path_saved_urls_file(self.uid)
          with open(path_saved_file, 'w+') as f:
               for url in self.checked_list:
                    f.write(url + '\n')

     def is_video_checked(self,url):
          return url in self.checked_list    

     def process_todelete(self):
          if len(self.todelete_data) > 0:
               for url in self.todelete_data:
                    if not self.is_video_todelete(url):
                         self.todelete_list.append(url)
                    else:
                         self.todelete_list.remove(url)
               self.write_todelete()
          
     def write_todelete(self):
          path_todelete_file = cfg.get_path_todelete_urls_file(self.uid)
          with open(path_todelete_file, 'w+') as f:
               for url in self.todelete_list:
                    f.write(url + '\n')

     def is_video_todelete(self,url):
          return url in self.todelete_list    


def get_form_data():
     data={}

# Create instance of FieldStorage 
     form = cgi.FieldStorage() 

# Get data from fields
     value_offset = form.getvalue('offset')
     data['offset'] = value_offset and int(value_offset) or 0
     data['url_id'] = form.getvalue('uid') or 0
     data['checkd'] = []
     data['delete'] = []

     for i in range(1, cfg.videos_on_page):
          val = form.getvalue('vid_num_'+str(i-1))
          if val:
               data['checkd'].append(val)
          else: 
               val = form.getvalue('del_vid_num_'+str(i-1))
               if val:
                    data['delete'].append(val)

     return data

if __name__ == '__main__':
     form_data = get_form_data()
     current_page = Page(form_data)
     current_page.present()
