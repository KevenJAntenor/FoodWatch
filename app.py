from flask import Flask, render_template, request, redirect, url_for, jsonify
from database import Database
from math import ceil
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
from scripts.sync_data import synchronize_data

app = Flask(__name__)


scheduler = BackgroundScheduler()
scheduler.add_job(func=synchronize_data, trigger="cron", hour=0)
scheduler.start()

atexit.register(lambda: scheduler.shutdown())


@app.route('/contrevenants', methods=['GET'])
def get_violations_between_dates():
    du = request.args.get('du', default=None)
    au = request.args.get('au', default=None)


    if not du or not au:
        return jsonify({'error': 'Both start and end dates must be provided.'}), 400


    db = Database()
    violations = db.get_violations_between_dates(du, au)


    return jsonify(violations)

@app.route('/doc')
def documentation():
    return render_template('doc.html')

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

@app.route('/restaurant_names')
def restaurant_names():
    db = Database()
    names = db.get_restaurant_names()
    return jsonify(names)

@app.route('/infractions_par_restaurant', methods=['GET'])
def infractions_par_restaurant():
    nom_restaurant = request.args.get('nom', type=str)
    if not nom_restaurant:
        return jsonify({'error': 'Restaurant name is required.'}), 400

    db = Database()
    infractions = db.get_infractions_by_restaurant(nom_restaurant)
    return jsonify(infractions)



if __name__ == '__main__':
    app.run(use_reloader=False)
