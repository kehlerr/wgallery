import json
from datetime import datetime
from flask import render_template, request, url_for, redirect

from wgallery import app
import config as cfg
from promotion import PageData, PromoteRequestHandler, CommitRequestHandler
from catalog_json import CatalogJSON
from index_view import IndexView


app.add_url_rule('/', view_func=IndexView.as_view('index'))


@app.route('/promote/<string:uid>', methods=['GET', 'POST'])
def promote(uid):
    if request.method == 'POST':
        request_data = request.form
    else:
        request_data = request.args

    catalog_obj = CatalogJSON(uid)
    request_handler = PromoteRequestHandler(request_data, catalog_obj)
    request_handler.handle()
    page = PageData(catalog_obj, request_handler)
    page.update_catalog_in_db()
    return render_template('promote.html', page=page)


@app.route('/commit/<string:uid>')
def commit(uid):
    catalog_obj = CatalogJSON(uid)
    request_handler_obj = CommitRequestHandler(request.args, catalog_obj)
    request_handler_obj.handle()
    return redirect(
        url_for('promote', uid=uid, srcl=request.form.get('srcl'))
    )
