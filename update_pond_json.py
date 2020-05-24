import os, sys
import json
import config as cfg


def update_pond(pond_uid):
	pond_json_fname = cfg.get_json_pond_file(pond_uid)
	if not os.path.exists(pond_json_fname):
		print('pond json not exists!')
		exit(-1)

	with open(pond_json_fname, 'r') as fp:
		json_data = json.load(fp)
		json_data['info'] = {
			'uid': pond_uid,
			'overall_count': len(json_data['overall']),
			'promo_count': len(json_data['promo']),
			'todel_count': len(json_data['todel']),
			'type': 'type' in json_data and json_data['type'] or 'default'
		}

	with open(pond_json_fname, 'w+') as fp:
		json.dump(json_data, fp, separators=(',',':'))

	cfg.update_ponds_db(pond_uid, json_data['info'])

	print(f'pond updated: {pond_uid}')


if __name__ == "__main__":
	dir_name = sys.argv[1]
	if not dir_name:
		print('need dir_name!')
		exit(-1)

	dir_path = cfg.wip_path + dir_name
	if not os.path.exists(dir_path) or not os.path.isdir(dir_path):
		print('wrong directory: %s!!!') % dir_name
		exit(-1)

	update_pond(dir_name)

