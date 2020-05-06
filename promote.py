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
          self.posts_count = len(self.json_list)


     def fill_json_list(self):
          filename = cfg.get_path_json_urls_file(self.uid)
          if os.path.exists(filename):
               with open(filename, 'r') as f:
                    self.json_list = json.load(f)

     def fill_checked_list(self):
          path_saved_file = cfg.get_path_saved_urls_file(self.uid)
          if os.path.exists(path_saved_file):
               with open(path_saved_file, 'r') as f:
                    self.checked_list = f.read().splitlines()

     def fill_todelete_list(self):
          path_todelete_file = cfg.get_path_todelete_urls_file(self.uid)
          if os.path.exists(path_todelete_file):
               with open(path_todelete_file, 'r') as f:
                    self.todelete_list = f.read().splitlines()


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
                         <link rel="stylesheet" type="text/css" href="css/post_cell.css"/>
                    </head>'''

     def present_body(self):
          print '''<body style="font-family:'Roboto',Verdana,Geneva,sans-serif">'''

          self.create_main_form()
          self.create_navigations_refs()
 
          print "</body>"
          print "</html>"

     def create_main_form(self):
          print '''<form action="/cgi-enabled/promote.py" method="POST">'''
          self.create_info_count()
          print '''<div class="grid-container">'''
          self.create_videos()
          print '''</div>'''
          print '''
          <div style="margin-top:10px">
               <span style="margin-left: 35%;margin-top: 0px;">
                    <input class="enjoy-css" type="submit" name="back" value="<<">
                    <script type="text/javascript" script-name="syncopate" src="http://use.edgefonts.net/syncopate.js"></script>
               </span>
               <span>
                    <input class="enjoy-css" name="next" type="submit" value="Submit>">
                    <script type="text/javascript" script-name="syncopate" src="http://use.edgefonts.net/syncopate.js"></script>
               </span>
          </div>'''
          print '''   <input type="hidden" name="offset" value="%d">''' % self.offset
          print '''   <input type="hidden" name="uid" value="%s">''' % self.uid
          print ''' </form> '''

     def create_info_count(self):
          print ''' <div style="background-color:#b5e270;font-size: larger;margin-bottom: 5px;margin-right: 7;border-radius: 7px;padding: 5px;padding-left: 10px;"> '''
          print '''<b><span style="color:darkslategrey">Total posts: %d</span></b>''' % (self.posts_count)
          checked_count = len(self.checked_list)
          if checked_count > 0:
               print '''<span style="color:green">/ checked: <b>%d</b></span>''' % (checked_count)

          todelete_count = len(self.todelete_list)
          if todelete_count > 0:
               print '''<span style="color:red">/ todelete: <b>%d</b></span>''' % (todelete_count)
          print ''' </div> '''

     def create_videos(self):
          videos_on_page = min(cfg.videos_on_page, self.posts_count - self.offset-1)
          for i in range(videos_on_page):
               self.create_video_field(i)

     def create_video_field(self, idx):
          vid_num = self.offset + idx+1
          post_data = self.get_data_by_number(vid_num)
          if not post_data:
               return
          url=''
          vid_post = ''
          if 'local_filename' in post_data:
               fname = post_data['local_filename']
               url = os.path.join(cfg.url_path, self.uid, fname)
               vid_post = fname
          else:
               url = post_data['videoUrl'].split('?')[0]
               vid_post = url
          poster_uid='posterUid' in post_data and post_data['posterUid'] or 0
          like_count='likeCount' in post_data and post_data['likeCount'] or 0
          comment_count='commentCount' in post_data and post_data['commentCount'] or 0
          item_class = 'post-cell'
          if self.is_video_checked(vid_post):
               item_class = 'post-cell_promoted'
          elif self.is_video_todelete(vid_post):
               item_class = 'post-cell_deleted'

          print '''<div class="%s">''' % (item_class)
          print ''' 
          <div class="sidebar_left">
               <label class="container" style="margin-top:200px">
                    <input type="checkbox" name="del_vid_num_%s" value="%s">
                    <span class="checkmark_todel"></span>
               </label>
          </div>''' % (str(idx), vid_post)
          print '''
          <div class="content">
               <video width="220" height="360" controls="">
                    <source src="%s" type="video/mp4">
               </video>
          </div>''' % url
          print '''<div class="sidebar_right_top">'''
          if poster_uid != 0:
               print '''
               <div>
                 <img style="margin-left:auto;margin-right: auto;display:block" src="img/icon_like.png">
                 <span style="display:block;text-align:center">%s</span>
               </div>''' % like_count
               print '''
               <div> 
                 <img style="margin-left:auto;margin-right: auto;display:block" src="img/icon_comment.png">
                 <span style="display:block;text-align:center">%s</span>
               </div>''' % comment_count
          print ''' </div> '''
          print '''<div class="sidebar_right">
          <div style="margin-top:10px">
            <label class="container">
               <input type="checkbox" name="vid_num_%s" value="%s">
               <span class="checkmark_promote"></span>
            </label></div>
          </div>''' % (str(idx), vid_post)
          if poster_uid != 0:
               print '''
                    <div class="footer">
                         <span style="display:block;text-align:center;margin-top:10px">%s</span>
                    </div>''' % (poster_uid)
          print '''</div>'''

     def get_data_by_number(self, n):
          number_in_list = n > 0 and n < self.posts_count
          return number_in_list and self.json_list[n-1]['data'][0] or None

     def create_navigations_refs(self):
          print ''' <table> <tbody> <tr valign="top"> '''

          current_page_idx = self.offset / cfg.videos_on_page + 1
          left_idx = max(0, current_page_idx - cfg.max_refs_count/2+1)
          refs_count = min(self.posts_count / cfg.videos_on_page + 1 - left_idx, cfg.max_refs_count)
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

     def is_video_checked(self,v):
          return v in self.checked_list

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
     offset_change = 0
     if form.getvalue('back'):
          offset_change = -1
     elif form.getvalue('next'):
          offset_change = 1

     value_offset = form.getvalue('offset')
     curr_offset = value_offset and int(value_offset) or 0
     data['offset'] = curr_offset + cfg.videos_on_page*offset_change
     data['url_id'] = form.getvalue('uid') or 0
     data['checkd'] = []
     data['delete'] = []

     for i in range(cfg.videos_on_page):
          val = form.getvalue('vid_num_'+str(i))
          if val:
               data['checkd'].append(val)
          else: 
               val = form.getvalue('del_vid_num_'+str(i))
               if val:
                    data['delete'].append(val)

     return data

if __name__ == '__main__':
     form_data = get_form_data()
     current_page = Page(form_data)
     current_page.present()
