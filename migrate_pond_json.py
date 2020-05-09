#!/usr/bin/python

import os, sys
import json
import config as cfg

if __name__ == "__main__":
	dir_name = sys.argv[1]
	if not dir_name:
		print('need dir_name!')
		exit(-1)

	dir_path = cfg.wip_path + dir_name
	if not os.path.exists(dir_path) or not os.path.isdir(dir_path):
		print('wrong directory!!!')
		exit(-1)


	pond_json_fname = cfg.get_json_pond_file(dir_name)
	json_exists = os.path.exists(pond_json_fname)
	os.chdir(dir_path)
	files_list = sorted(filter(os.path.isfile, os.listdir('.')), key=os.path.getmtime)
	json_data = {'posts':{}, 'overall':[], 'promo':[], 'todel':[]}

	if json_exists and len(files_list) <= 3:
		old_json_data = []
		with open(pond_json_fname, 'r') as fp:
			old_json_data = json.load(fp)

		exctract_json_keys = [
			"postTime",
			"msgText",
			"videoTitle",
			"likeCount",
			"commentCount",
			"quality",
			"playCount",
			"musicId",
			"posterUid",
			"shareCount",
			"nickName",
			"videoWidth",
			"postId",
			"videoHeight",
			"sound/soundId",
			"videoUrl",
			"downloadCount",
			"duet"
		]

		for p in old_json_data:
			if not 'data' in p or len(p['data']) < 1:
				continue
			p_data = p['data'][0]
			exctracted_new_post = {}
			for k in exctract_json_keys:
				key = k
				value = key in p_data and p_data[key]
				keys = k.split('/')
				if len(keys) > 1:
					key = keys[1]
					value = p_data[keys[0]][key]
				exctracted_new_post[key] = value
			postId = exctracted_new_post['postId']
			json_data['posts'][postId] = exctracted_new_post
			json_data['overall'].append(postId)
	else:
		for fname in files_list:
			if cfg.is_video(fname):
				video_url = os.path.join(cfg.url_path, dir_name, fname)
				data = { "videoUrl": video_url, "local_filename":fname, "postId":fname }
				json_data['posts'][fname] = data
				json_data['overall'].append(fname)

	print('migrate pond:' + dir_name)
	with open(dir_name + '.json', 'w+') as fp:
		json.dump(json_data, fp, separators=(',',':'))
