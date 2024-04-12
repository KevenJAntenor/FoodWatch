import uuid
from flask import Flask, flash, render_template, request, redirect, session, url_for, jsonify, Response
from database import Database
from math import ceil
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
from scripts.sync_data import synchronize_data
from dicttoxml import dicttoxml
from io import StringIO
import csv
from jsonschema import validate, ValidationError
import json

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
    return render_template('api_documentation.html')


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

    return render_template('results.html', rows=rows, total_pages=total_pages, current_page=page,
                           search_term=search_term, search_by=search_by)


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


@app.route('/establishments')
def get_establishments():
    db = Database()
    establishments = db.get_establishments_with_infractions()
    return jsonify(establishments)


@app.route('/establishments_xml')
def establishments_xml():
    db = Database()
    establishments = db.get_establishments_with_infractions()

    xml = dicttoxml(establishments, custom_root='establishments', attr_type=False)
    return Response(xml, mimetype='application/xml; charset=utf-8')


@app.route('/establishments_csv')
def establishments_csv():
    db = Database()
    establishments = db.get_establishments_with_infractions()

    si = StringIO()
    writer = csv.writer(si)

    writer.writerow(['Etablissement', 'Nombre d\'Infractions'])

    for establishment in establishments:
        writer.writerow([establishment['etablissement'], establishment['infraction_count']])

    si.seek(0)

    return Response(si.getvalue(), mimetype='text/csv', headers={"Content-Disposition": "attachment;filename"
                                                                                        "=establishments.csv"})


@app.route('/demande_inspection', methods=['POST'])
def demande_inspection():
    with open('schemas/inspection_request_schema.json') as schema_file:
        schema = json.load(schema_file)

    request_data = request.get_json()

    try:
        validate(instance=request_data, schema=schema)

        establishment = request_data['nom_etablissement']
        address = request_data['adresse']
        city = request_data['ville']
        visit_date = request_data['date_visite']
        last_name = request_data['nom_client']
        first_name = request_data['prenom_client']
        description = request_data['description_probleme']

        db = Database()
        db.insert_inspection_request(establishment, address, city, visit_date, last_name, first_name, description)

        return jsonify({"message": "Demande d'inspection reçue avec succès."}), 200
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400


@app.route('/complaint')
def complaint():
    return render_template('complaint.html')


@app.route('/create_user_profile', methods=["GET", "POST"])
def create_user_profile():
    with open('schemas/user_profile_schema.json', 'r') as schema_file:
        user_profile_schema = json.load(schema_file)

    if request.method == "GET":
        establishments = get_establishments()
        return render_template("register_new_profile.html", establishments=establishments), 200
    else:

        try:
            validate(instance=request.json, schema=user_profile_schema)
        except ValidationError as e:
            flash("Erreur de validation du document JSON: {}".format(e.message))
            return redirect(url_for("create_user_profile"))

        nom = request.form.get("nom")
        courriel = request.form.get("courriel")
        mdp = request.form.get("mdp")
        selectedEstablishments = request.form.get("selectedEstablishments")

        db = Database()
        conn = db.get_connection()
        cursor = conn.cursor()
        existing_user = cursor.execute(
            "SELECT * FROM utilisateurs WHERE email = ?", (courriel,)
        ).fetchone()

        if existing_user:
            flash("Un utilisateur avec cette adresse e-mail existe déjà.")
            return redirect(url_for("create_user_profile"))

        try:

            cursor.execute(
                "INSERT INTO utilisateurs (nom_complet, email, password) VALUES (?, ?, ?)",
                (nom, courriel, mdp)
            )
            conn.commit()

            user_id = cursor.lastrowid

            selected_establishments = json.loads(selectedEstablishments)
            for establishment in selected_establishments:
                cursor.execute(
                    "INSERT INTO utilisateurs_etablissements (utilisateur_id, nom_etablissement) VALUES (?, ?)",
                    (user_id, establishment)
                )
            conn.commit()

            # flash("Le nouvel utilisateur a été créé avec succès.")
            return redirect("/user_profile_home") 

        except Exception as e:
            flash("Une erreur s'est produite lors de la création de l'utilisateur.")
            print(e) 
            conn.rollback()

        finally:
            cursor.close()
            conn.close()

        return render_template("register_new_profile.html")  


@app.route("/login", methods=["GET", "POST"])
def login_user():
    if request.method == "GET":
        return render_template("login.html"), 200
    else:
        # Update the error message for email/password combination
        error_message = "Email and/or Password incorrect!"
        email = request.form["email"]
        password = request.form["password"]

        # Database connection
        db = Database()
        conn = db.get_connection()
        cursor = conn.cursor()

        user = cursor.execute(
            "SELECT password FROM utilisateurs WHERE email = ?", (email,)
        ).fetchone()

        if user is None:
            cursor.close()
            conn.close()
            flash(error_message)
            return render_template("login.html", error_message=error_message), 404

        if password == user[0]:
            # Access granted, create session
            id_session = uuid.uuid4().hex
            cursor.execute(
                "INSERT INTO sessions (id_session, utilisateur) VALUES (?, ?)",
                (id_session, email),
            )
            conn.commit()
            cursor.close()
            conn.close()
            session["user"] = id_session
            return redirect("/user_profile_home")

        else:
            cursor.close()
            conn.close()
            flash(error_message)
            return render_template("login.html", error_message=error_message), 404
        
@app.route('/user_profile_home')
def user_profile_home():
    # db = Database()
    # conn = db.get_connection()
    # cursor = conn.cursor()

    # user = cursor.execute(
    #     "SELECT nom_etablissement FROM utilisateurs_etablissements WHERE utilisateur_id = ?", (email,)
    # ).fetchone()
    return render_template('user_profile_home.html')


if __name__ == '__main__':
    app.run(use_reloader=False)
