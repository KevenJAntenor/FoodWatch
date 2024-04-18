import csv
import hashlib
import sqlite3
import uuid
import requests
import yaml


DATA_URL = 'https://data.montreal.ca/dataset/05a9e718-6810-4e73-8bb9-5955efeb91a0/resource/7f939a08-be8a-45e1-b208-d8744dca8fc6/download/violations.csv'
DATABASE = 'db/db.db'

CONFIG_ADMIN_FILE = 'config_admin.yaml'

def read_admin_info_from_yaml(file_path):
    with open(file_path, 'r') as yaml_file:
        admin_info = yaml.safe_load(yaml_file)
    return admin_info

admin_info = read_admin_info_from_yaml(CONFIG_ADMIN_FILE)


response = requests.get(DATA_URL)
response.raise_for_status()


with open('violations.csv', 'w', encoding='utf-8') as file:
    file.write(response.text)

conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()


# Insert admin user
hashed_password = hashlib.sha512((admin_info['password'] + admin_info['salt']).encode('utf-8')).hexdigest()
cursor.execute("""
    INSERT INTO utilisateurs (nom_complet, email, hashed_password, salt, role)
    VALUES (?, ?, ?, ?, ?)
""", (admin_info['nom_complet'], admin_info['email'], hashed_password, admin_info['salt'], 'admin'))



with open('violations.csv', 'r', encoding='utf-8') as csvfile:
    csv_reader = csv.reader(csvfile)
    next(csv_reader)
    for row in csv_reader:
        cursor.execute("""
            INSERT INTO violations (
                id_poursuite, business_id, date, description, adresse, date_jugement,
                etablissement, montant, proprietaire, ville, statut, date_statut, categorie
            ) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, row)

conn.commit()
conn.close()

print('Data has been downloaded and inserted into the database.')
