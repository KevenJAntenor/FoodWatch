import csv
import sqlite3
import requests


DATA_URL = 'https://data.montreal.ca/dataset/05a9e718-6810-4e73-8bb9-5955efeb91a0/resource/7f939a08-be8a-45e1-b208-d8744dca8fc6/download/violations.csv'


DATABASE = '../db/db.db'


response = requests.get(DATA_URL)
response.raise_for_status()

with open('violations.csv', 'wb') as file:
    file.write(response.content)

conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()

with open('violations.csv', 'r') as csvfile:
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
