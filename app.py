from flask import Flask, render_template, request, url_for
from index import get_ponds
import promotion

app = Flask(__name__)

# not for prod
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


@app.route('/')
def index():
    t = request.args.get('type', default = None, type = str)
    return render_template('index.html', ponds=get_ponds(t))

@app.route('/promote/<string:uid>', methods=['GET', 'POST'])
def promote(uid):
    if request.method == 'POST':
        request_data = request.form
    else:
        request_data = request.args

    pond_obj = promotion.PondJSON(uid)
    request_handler_obj = promotion.RequestHadler(request_data, pond_obj)
    request_handler_obj.handle()
    page = promotion.PageData(pond_obj, request_handler_obj)
    return render_template('promote.html', page=page)

if __name__ == '__main__':
    app.run(debug=True)