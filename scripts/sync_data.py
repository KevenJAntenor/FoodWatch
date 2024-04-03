import csv
import sqlite3
import requests

def synchronize_data():
    DATA_URL = 'https://data.montreal.ca/dataset/05a9e718-6810-4e73-8bb9-5955efeb91a0/resource/7f939a08-be8a-45e1-b208-d8744dca8fc6/download/violations.csv'
    DATABASE = 'db/db.db'

    response = requests.get(DATA_URL)
    response.raise_for_status()

    lines = response.iter_lines()
    reader = csv.reader(line.decode('utf-8') for line in lines)
    next(reader)

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()

        cursor.execute("DELETE FROM violations")


        for row in reader:
            cursor.execute("""
                INSERT INTO violations (
                    id_poursuite, business_id, date, description, adresse, date_jugement,
                    etablissement, montant, proprietaire, ville, statut, date_statut, categorie
                ) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, row)

        conn.commit()

    print('Data has been synchronized.')
