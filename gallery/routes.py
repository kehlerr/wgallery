import json
from datetime import datetime
from flask import render_template, request, url_for, redirect, views

from gallery import app, db, models

import config as cfg

import common_forms
import promotion
import pond_json as pj
from generate_pond_json import update_pond


class IndexView(views.MethodView):
    methods = ['GET', 'POST']
    last_seen_max = 15

    def __init__(self):
        super(IndexView, self).__init__()
        self.types_list = models.get_all_types()
        self.ponds_list = models.filter_and_get_ponds()
        self.ponds = self.ponds_list
        self.ponds_type = None
        self.ponds_category = None
        self.categories_list = None
        self.categories_by_type = {}
        self.fill_categories()
        self.new_ponds = None
        self.deleted_ponds = None
        self.last_seen_ponds = None
        self.types_edit_form = None

    def fill_categories(self):
        for type_ in self.types_list:
            categories = models.get_categories_by_type(
                name_id=type_
            )
            self.categories_by_type[type_] = categories

    def get(self):
        form = request.form
        self.types_edit_form = common_forms.EditModalForm(form)
        self.setup_ponds_on_request()
        return self.do_render()

    def post(self):
        form = request.form
        self.types_edit_form = common_forms.EditModalForm(form)
        pond_id = form.get('pond_id')
        updated_type = form.get('new_type_name') or form.get('pond_type')
        updated_category = (form.get('new_category_name') or
                            form.get('pond_category') or '')
        update_pond(pond_id, updated_type, updated_category)
        return redirect(url_for('index'))

    def setup_ponds_on_request(self):
        self.ponds_type = request.args.get('type', default=None, type=str)
        if self.ponds_type:
            self.ponds_category = request.args.get(
                'cat', default=None, type=str
            )
            self.categories_list = self.categories_by_type[self.ponds_type]
            self.ponds = models.filter_and_get_ponds(
                self.ponds_type,
                self.ponds_category
            )
        else:
            self.scan_for_new_ponds()
            self.fill_last_seen_ponds()
            self.ponds = self.ponds_list

    def do_render(self):
        return render_template(
            'index.html',
            ponds=self.ponds,
            categories_by_type=json.dumps(self.categories_by_type),
            categories=self.categories_list,
            type=self.ponds_type,
            types=self.types_list,
            new_ponds=self.new_ponds,
            last_seen_ponds=self.last_seen_ponds,
            form=self.types_edit_form
        )

    def scan_for_new_ponds(self):
        folders_in_db = {x.name_id for x in self.ponds_list}
        current_folders = {x.split('/')[-2] for x in cfg.get_folders_list()}
        self.new_ponds = list(current_folders.difference(folders_in_db))
        self.deleted_ponds = list(folders_in_db.difference(current_folders))

    def fill_last_seen_ponds(self):
        last_seen = []
        for p in self.ponds_list:
            if p.last_seen_at:
                last_seen.append(p)

        if not last_seen:
            return

        self.last_seen_ponds = sorted(
            last_seen,
            key=lambda v: v.last_seen_at.timestamp())[:self.last_seen_max]

app.add_url_rule('/', view_func=IndexView.as_view('index'))


@app.route('/promote/<string:uid>', methods=['GET', 'POST'])
def promote(uid):
    if request.method == 'POST':
        request_data = request.form
    else:
        request_data = request.args

    pond_obj = pj.PondJSON(uid)
    request_handler = promotion.PromoteRequestHandler(request_data, pond_obj)
    request_handler.handle()
    page = promotion.PageData(pond_obj, request_handler)
    page.update_pond_in_db()
    return render_template('promote.html', page=page)


@app.route('/commit/<string:uid>')
def commit(uid):
    pond_obj = pj.PondJSON(uid)
    request_handler_obj = promotion.CommitRequestHandler(request.args, pond_obj)
    request_handler_obj.handle()
    return redirect(
        url_for('promote', uid=uid, srcl=request.form.get('srcl'))
    )
