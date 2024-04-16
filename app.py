import base64
from functools import wraps
import uuid
from flask import Flask, abort, flash, render_template, request, redirect, session, url_for, jsonify, Response
from scripts.database import Database
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
# cle secrete pour les messages flash
app.config["SECRET_KEY"] = "secretKey"

scheduler = BackgroundScheduler()
scheduler.add_job(func=synchronize_data, trigger="cron", hour=0)
scheduler.start()

atexit.register(lambda: scheduler.shutdown())

@app.context_processor
def context_processor():
    return {'is_authenticated': is_authenticated()}



def authenticated_only(route_function):
    @wraps(route_function)
    def wrapper(*args, **kwargs):
        if is_authenticated():
            return route_function(*args, **kwargs)
        else:
            flash("Connectez-vous pour acceder a cette page !", "info")
            return render_template("index.html"), 401

    return wrapper


def is_authenticated():
    return 'user' in session




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
    
@app.route('/demande_inspection/<int:request_id>', methods=['DELETE'])
def delete_demande_inspection(request_id):
    if request.method == "DELETE":
        db = Database()
        try:
            result = db.delete_inspection_request(request_id)
            if result:
                return jsonify({"message": "La demande d'inspection a été supprimée avec succès."}), 200
            else:
                return jsonify({"error": "Demande d'inspection non trouvée."}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        abort(400)



@app.route('/complaint')
def complaint():
    return render_template('complaint.html')


@app.route('/create_user_profile', methods=["GET", "POST"])
def create_user_profile():
    with open('schemas/user_profile_schema.json', 'r') as schema_file:
        user_profile_schema = json.load(schema_file)

    if request.method == "GET":
        establishments = get_establishments()  
        return render_template("create_new_profile.html", establishments=establishments), 200
    else:

        nom = request.form['nom']
        courriel = request.form['courriel']
        mdp = request.form['mdp']
        selectedEstablishments = request.form['selectedEstablishments']

        request_data = {
            "nom": nom,
            "courriel": courriel,
            "mdp": mdp,
            "selectedEstablishments": json.loads(str(selectedEstablishments))
        }

        try:
            validate(instance=request_data, schema=user_profile_schema)
        except ValidationError as e:
            error_message ="Erreur de validation du document JSON: {}".format(e.message)
            return jsonify({'error': str(error_message), 'success': False}), 500
            # return render_template("create_new_profile.html", establishments=establishments), 00


        db = Database()
        existing_user = db.get_user_by_email(courriel)
        if existing_user:
            error_message = "Un utilisateur avec cette adresse e-mail existe déjà."
            return render_template("create_new_profile.html", error_message=error_message),409

        try:
            utilisateur_id = db.insert_user(nom, courriel, mdp)
            selected_establishments = json.loads(selectedEstablishments)
            db.insert_user_establishments(utilisateur_id, selected_establishments)
            return redirect(url_for('user_profile_home', utilisateur_id=utilisateur_id))

        except Exception as e:
            error_message = "Une erreur s'est produite lors de la création du profil utilisateur."
            return render_template("create_new_profile.html", error_message=error_message),409


@app.route("/login", methods=["GET", "POST"])
def login_user():
    if request.method == "GET":
        return render_template("login.html"), 200
    else:
        error_message = "Email and/or Password incorrect!"
        email = request.form["email"]
        password = request.form["password"]

        db = Database()

        utilisateur_id = db.verify_user_credentials(email, password)
        if utilisateur_id:
            id_session = uuid.uuid4().hex
            db.insert_session(id_session, email)  
            session["user"] = id_session
            return redirect(url_for('user_profile_home', utilisateur_id=utilisateur_id))
        else:
            return render_template("login.html", error_message=error_message), 404
        
@app.route("/logout")
@authenticated_only
def logout_user():
    if "user" in session:
        session_id = session["user"]
        db = Database()
        db.delete_session(session_id)
        session.pop("user", None)
        return redirect(url_for('login_user'))


@app.route('/user_profile_home/<int:utilisateur_id>', methods=["GET"])
@authenticated_only
def user_profile_home(utilisateur_id):
    db = Database()
    user = db.get_user_by_id(utilisateur_id)

    if user:
        establishments = db.get_user_profile_etablissements(utilisateur_id)
        if user[5]:
            image_base64 = base64.b64encode(user[5]).decode('utf-8')
            return render_template('user_profile_home.html', user=user, establishments=establishments, image_base64=image_base64)
        else:
            return render_template('user_profile_home.html', user=user, establishments=establishments, image_base64='')
    else:
        error_message = "L'utilisateur avec l'identifiant '" + str(utilisateur_id) + "' n'existe pas !"
        abort(404, error_message)

@app.route('/update_establishments/<int:utilisateur_id>', methods=["POST"])
@authenticated_only
def update_establishments(utilisateur_id):
    try:
        db = Database()
        selectedEstablishments = request.form.getlist('selectedEstablishments')  
        db.update_user_establishments(utilisateur_id, selectedEstablishments)

        flash("Mise à jour des vos établissements effectuée !")
        return redirect(url_for('user_profile_home', utilisateur_id=utilisateur_id))
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500




@app.route('/upload_profile_pic/<int:utilisateur_id>', methods=["POST"])
@authenticated_only
def upload_profile_pic(utilisateur_id):
    try:
        db = Database()

        photo_profil = request.files.get("photo_profil")
        db.update_user_photo_profile(utilisateur_id, photo_profil)

        flash("Photo de profil mise à jour avec succès !")
        return redirect(url_for('user_profile_home', utilisateur_id=utilisateur_id))
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/unsubscribe/<token>', methods=['GET', 'POST'])
def unsubscribe(token):
    try:
        token = request.args.get('token')
        establishment = request.args.get('establishment')
        if request.method == "GET":
            return render_template("unsubscribe.html", establishment=establishment), 200
        else:
            db = Database()
            db.delete_establishment_from_user_establishments(token, establishment)
            message =  "You have been unsubscribed from {}.\nIt's no longer under your surveillance.".format(establishment)
            return jsonify({'message': message}), 200
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500



@app.errorhandler(404)
def retourner404(err):
    return render_template("erreur.html", err="404", error_message=err), 404


@app.errorhandler(400)
def retourner400(err):
    return render_template("erreur.html", err="400", error_message=err), 400


@app.errorhandler(405)
def retourner500(err):
    return render_template("erreur.html", err="405", error_message=err), 405


if __name__ == '__main__':
    app.run(use_reloader=False)
