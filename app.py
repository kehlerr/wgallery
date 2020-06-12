from flask import Flask, render_template, request, url_for, redirect
import config as cfg
import promotion
import pond_json as pj

app = Flask(__name__)

# not for prod
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


@app.route('/')
def index():
    t = request.args.get('type', default=None, type=str)
    return render_template('index.html', ponds=cfg.get_ponds(t))


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
    return redirect(url_for('promote', uid=uid, srcl=request.form.get('srcl')))



if __name__ == '__main__':
    app.run(debug=True)
