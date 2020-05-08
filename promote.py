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
          self.src_list = form_data['src_list'] or 'overall'

          self.json_pond = {}
          self.json_pond_fname = cfg.get_json_pond_file(self.uid)
          self.load_json_pond()

          self.posts = self.json_pond['posts']
          self.overall = self.json_pond['overall']
          self.promo = self.json_pond['promo']
          self.todel = self.json_pond['todel']

          self.process_checked(form_data['promo'], 'promo')
          self.process_checked(form_data['todel'], 'todel')
          self.dump_pond()

          self.posts_count = len(self[self.src_list])
          self.offset = form_data['offset']
          if self.offset > self.posts_count or self.offset < 0:
               self.offset = form_data['prev_offset']
          self.posts_on_page_count = min(cfg.videos_on_page, self.posts_count - self.offset)

     def __getitem__(self, item):
          return getattr(self, item)

     def load_json_pond(self):
          if os.path.exists(self.json_pond_fname):
               with open(self.json_pond_fname, 'r') as fp:
                    self.json_pond = json.load(fp)

     def process_checked(self, data, l_type):
          if len(data) > 0:
               for n in data:
                    post = self.get_post_by_number(int(n), self.src_list)
                    lst = self[l_type]
                    if not self.is_post_checked(post, l_type):
                        lst.append(post['postId'])
                    else:
                        lst.remove(post['postId'])

     def dump_pond(self):
          with open(self.json_pond_fname, 'w+') as fp:
               json.dump(self.json_pond, fp)

     def is_post_checked(self, p, l_type):
          lst = self[l_type]
          return p['postId'] in lst

     def get_post_by_number(self, n, l_type):
          lst = self[l_type]
          number_in_list = n >= 0 and n <= len(lst)
          if number_in_list:
               postId = lst[n]
               if postId:
                    return self.posts[postId]


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
          print '''<form id="main" action="/cgi-enabled/promote.py" method="POST">'''
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
          if self.src_list != 'overall':
               print '''   <input type="hidden" name="srcl" value="%s">''' % self.src_list
          print ''' </form> '''

     def create_info_count(self):
          print ''' <div style="background-color:#b5e270;font-size: larger;margin-bottom: 5px;margin-right: 7;border-radius: 7px;padding: 5px;padding-left: 10px;"> '''
          print '''<b>
          <a style="text-decoration-color:darkslategrey"
               href=promote.py?uid=%s>''' % self.uid
          overall_count = len(self.overall)
          print '''<span style="color:darkslategrey">Total posts: %d</span></a></b>''' % (overall_count)
          checked_count = len(self.promo)
          if checked_count > 0:
               print '''<a style="text-decoration-color:green"
               href=promote.py?uid=%s&srcl=promo>''' % self.uid
               print ''' <span style="color:green">/ checked: <b>%d</b></span></a>''' % (checked_count)

          todelete_count = len(self.todel)
          if todelete_count > 0:
               print '''<a style="text-decoration-color:#e01632"
               href=promote.py?uid=%s&srcl=todel>''' % self.uid
               print '''<span style="color:#e01632">/ todelete: <b>%d</b></span></a>''' % (todelete_count)
          print ''' </div> '''

     def create_videos(self):
          for i in range(self.posts_on_page_count):
               self.create_video_field(i)

     def create_video_field(self, idx):
          vid_num = self.offset + idx
          post_data = self.get_post_by_number(vid_num, self.src_list)
          if not post_data:
               return
          url=''
          if 'local_filename' in post_data:
               fname = post_data['local_filename']
               url = os.path.join(cfg.url_path, self.uid, fname)
          else:
               url = post_data['videoUrl'].split('?')[0]

          poster_uid='posterUid' in post_data and post_data['posterUid'] or 0
          like_count='likeCount' in post_data and post_data['likeCount'] or 0
          comment_count='commentCount' in post_data and post_data['commentCount'] or 0
          item_class = 'post-cell'
          if self.is_post_checked(post_data, 'promo'):
               item_class = 'post-cell_promoted'
          elif self.is_post_checked(post_data, 'todel'):
               item_class = 'post-cell_deleted'

          print '''<div class="%s">''' % (item_class)
          print ''' 
          <div class="sidebar_left">
               <label class="container" style="margin-top:200px">
                    <input type="checkbox" name="del_vid_num_%d" value="%d">
                    <span class="checkmark_todel"></span>
               </label>
          </div>''' % (idx, vid_num)
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
               <input type="checkbox" name="vid_num_%d" value="%d">
               <span class="checkmark_promote"></span>
            </label></div>
          </div>''' % (idx, vid_num)
          print '''
          <div class="footer">
               <span style="display:block;text-align:center;padding-top:12px;color: #5d5d5d;font-size: small;">
                    <b>%s</b>
               </span>
          </div>''' % (poster_uid != 0 and poster_uid or fname)
          print '''</div>'''


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
          offset = idx*cfg.videos_on_page
          if offset != self.offset:
               href = '''promote.py?offset=%d&uid=%s&srcl=%s''' % (offset, self.uid, self.src_list)
               print '''<a aria-label="%s" href="%s">''' % (offset, href)
               print offset
               print "</a>"
          else:
               print offset
               print "</td>"


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

     data['src_list'] = form.getvalue('srcl')
     value_offset = form.getvalue('offset')
     prev_offset = value_offset and int(value_offset) or 0
     curr_offset = prev_offset + cfg.videos_on_page*offset_change
     data['prev_offset'] = prev_offset
     data['offset'] = curr_offset
     data['url_id'] = form.getvalue('uid') or 0
     data['promo'] = []
     data['todel'] = []

     for i in range(cfg.videos_on_page):
          val = form.getvalue('vid_num_'+str(i))
          if val:
               data['promo'].append(val)
          else: 
               val = form.getvalue('del_vid_num_'+str(i))
               if val:
                    data['todel'].append(val)

     return data

if __name__ == '__main__':
     form_data = get_form_data()
     current_page = Page(form_data)
     current_page.present()
