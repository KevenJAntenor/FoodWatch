from flask import Flask, render_template, request, redirect, url_for
from database import Database
from math import ceil


app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        search_term = request.form.get('search_term')
        search_by = request.form.get('search_by')
        return redirect(url_for('search_results', search_by=search_by, search_term=search_term))
    return render_template('index.html')

@app.route('/search_results/<search_by>/<search_term>')
def search_results(search_by, search_term):
    db = Database()

    page = request.args.get('page', 1, type=int)
    per_page = 10

    rows, total_count = db.get_search_results_with_pagination(search_by, search_term, page, per_page)
    total_pages = ceil(total_count / per_page)

    return render_template('results.html', rows=rows, total_pages=total_pages, current_page=page, search_term=search_term, search_by=search_by)

if __name__ == '__main__':
    app.run(debug=True)
