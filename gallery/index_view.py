import json
from flask import render_template, request, url_for, redirect, views

import config as cfg
from gallery import models
import common_forms
from generate_catalog_json import update_catalog


class IndexView(views.MethodView):
    '''
        View for main page with links on all available catalogs
    '''
    methods = ['GET', 'POST']
    last_seen_max = 15

    def __init__(self):
        super(IndexView, self).__init__()
        self.types_list = models.get_all_types()
        self.catalogs_list = models.filter_and_get_catalogs()
        self.catalogs = self.catalogs_list
        self.catalogs_type = None
        self.catalogs_category = None
        self.categories_list = None
        self.categories_by_type = {}
        self.fill_categories()
        self.new_catalogs = None
        self.deleted_catalogs = None
        self.last_seen_catalogs = None
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
        self.setup_catalogs_on_request()
        return self.do_render()

    def post(self):
        form = request.form
        self.types_edit_form = common_forms.EditModalForm(form)
        catalog_id = form.get('catalog_id')
        updated_type = form.get('new_type_name') or form.get('catalog_type')
        updated_category = (form.get('new_category_name') or
                            form.get('catalog_category', ''))
        update_catalog(catalog_id, updated_type, updated_category)
        return redirect(url_for('index'))

    def setup_catalogs_on_request(self):
        self.catalogs_type = request.args.get('type', default=None, type=str)
        if self.catalogs_type:
            self.catalogs_category = request.args.get(
                'cat', default=None, type=str
            )
            self.categories_list = self.categories_by_type[self.catalogs_type]
            self.catalogs = models.filter_and_get_catalogs(
                self.catalogs_type,
                self.catalogs_category
            )
        else:
            self.scan_for_new_catalogs()
            self.fill_last_seen_catalogs()
            self.catalogs = self.catalogs_list

    def do_render(self):
        return render_template(
            'index.html',
            catalogs=self.catalogs,
            categories_by_type=json.dumps(self.categories_by_type),
            categories=self.categories_list,
            type=self.catalogs_type,
            types=self.types_list,
            new_catalogs=self.new_catalogs,
            last_seen_catalogs=self.last_seen_catalogs,
            form=self.types_edit_form
        )

    def scan_for_new_catalogs(self):
        folders_in_db = {x.name_id for x in self.catalogs_list}
        current_folders = {x.split('/')[-2] for x in cfg.get_folders_list()}
        self.new_catalogs = list(current_folders.difference(folders_in_db))
        self.deleted_catalogs = list(folders_in_db.difference(current_folders))

    def fill_last_seen_catalogs(self):
        last_seen = []
        for p in self.catalogs_list:
            if p.last_seen_at:
                last_seen.append(p)

        if not last_seen:
            return

        self.last_seen_catalogs = sorted(
            last_seen,
            key=lambda v: v.last_seen_at.timestamp())[:self.last_seen_max]
