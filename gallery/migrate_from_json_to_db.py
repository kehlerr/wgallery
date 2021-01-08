#!/usr/bin/python3.8

import os
import json
from datetime import datetime

from gallery import db, models
from config import wip_path


def get_ponds_db():
    return os.path.join(wip_path, 'ponds_db.json')


def get_ponds(pond_type=None, pond_category=None):
    ponds = []
    with open(get_ponds_db(), 'r') as fp:
        db_json = json.load(fp)
        for v in db_json['ponds']:
            pond = db_json['ponds'][v]
            if not pond_type or pond_type == pond['type']:
                if not pond_category or pond_category == pond.get('category'):
                    ponds.append(pond)

    sort_ponds = sorted(ponds, key=lambda i: i['overall_count'])
    return sort_ponds


ponds = get_ponds()

default_folder_path = '/home/kehlerr/datadump/.promodump/likee_wip/'

db.drop_all()
db.create_all()

t_p = models.PondType(name_id='profile')
db.session.add(t_p)
t_s = models.PondType(name_id='sound')
db.session.add(t_s)
t_c = models.PondType(name_id='custom')
db.session.add(t_c)
db.session.commit()

t = models.PondCategory(name_id='horny', pond_type_id=t_s.id)
db.session.add(t)
t = models.PondCategory(name_id='gym',  pond_type_id=t_s.id)
db.session.add(t)
t = models.PondCategory(name_id='ass_trend',  pond_type_id=t_s.id)
db.session.add(t)
t = models.PondCategory(name_id='loli', pond_type_id=t_p.id)
db.session.add(t)
t = models.PondCategory(name_id='preteen', pond_type_id=t_p.id)
db.session.add(t)
t = models.PondCategory(name_id='teen', pond_type_id=t_p.id)
db.session.add(t)

db.session.commit()

tstamp = datetime.now().timestamp()
last_seen_at = None

for p in ponds:
    last_seen_at = None
    last_post = p.get('last_post')
    if last_post:
        tstamp += 1
        last_seen_at = datetime.fromtimestamp(tstamp)

    entry = models.Pond(
        name_id=p['uid'],
        uid=p['uid'],
        promo_count=p['promo_count'],
        todel_count=p['todel_count'],
        overall_count=p['overall_count'],
        type=models.PondType.query.filter_by(name_id=p['type']).first().id,
        last_post=p.get('last_post'),
        last_offset=p.get('last_offset'),
        fpath=default_folder_path + p['uid'],
        category=p.get('category'),
        last_seen_at=last_post and last_seen_at or None
    )
    db.session.add(entry)

db.session.commit()
