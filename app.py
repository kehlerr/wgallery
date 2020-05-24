from flask import Flask, render_template, request, url_for
from index import get_ponds
import promote_page

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
        form_data = promote_page.get_promote_data(request.form)
    else:
        form_data = promote_page.get_promote_data(request.args)
    form_data['url_id'] = uid
    page = promote_page.Page(form_data)
    return render_template('promote.html', page=page)




if __name__ == '__main__':
    app.run(debug=True)