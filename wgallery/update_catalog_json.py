import os
import sys
import json
import config as cfg


def update_catalog(catalog_uid):
    catalog_json_fname = cfg.get_json_catalog_file(catalog_uid)
    if not os.path.exists(catalog_json_fname):
        print('catalog json not exists!')
        exit(-1)

    with open(catalog_json_fname, 'r') as fp:
        json_data = json.load(fp)
        json_data['info'] = {
            'uid': catalog_uid,
            'overall_count': len(json_data['overall']),
            'promo_count': len(json_data['promo']),
            'todel_count': len(json_data['todel']),
            'type': 'type' in json_data and json_data['type'] or 'default'
        }

    with open(catalog_json_fname, 'w+') as fp:
        json.dump(json_data, fp, separators=(',', ':'))

    cfg.update_catalogs_db(catalog_uid, json_data['info'])

    print(f'catalog updated: {catalog_uid}')


if __name__ == "__main__":
    dir_name = sys.argv[1]
    if not dir_name:
        print('need dir_name!')
        exit(-1)

    dir_path = os.path.join(cfg.catalogs_root_path, dir_name)
    if not os.path.exists(dir_path) or not os.path.isdir(dir_path):
        print(f'wrong directory: {dir_name}!!!')
        exit(-1)

    update_catalog(dir_name)
