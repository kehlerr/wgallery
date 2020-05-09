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
		print('wrong directory: %s!!!') % dir_name
		exit(-1)

	pond_json_fname = cfg.get_json_pond_file(dir_name)
	if not os.path.exists(pond_json_fname):
		print('pond json not exists!')
		exit(-1)

	json_data = []

	with open(pond_json_fname, 'r') as fp:
		json_data = json.load(fp)
		json_data['info'] = {
			'uid': dir_name,
			'overall_count': len(json_data['overall']),
			'promo_count': len(json_data['promo']),
			'todel_count': len(json_data['todel'])
		}

	with open(pond_json_fname, 'w+') as fp:
		json.dump(json_data, fp, separators=(',',':'))

	db_json = []
	db_json_fname = cfg.get_ponds_db()
	with open(db_json_fname, 'r') as fp:
		db_json = json.load(fp)

	db_json['ponds'][dir_name] = json_data['info']

	with open(db_json_fname, 'w+') as fp:
		json.dump(db_json, fp, separators=(',',':'))

	print('pond updated:'+dir_name)

