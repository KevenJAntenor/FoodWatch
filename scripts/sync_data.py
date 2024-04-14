import csv
import sqlite3
import requests
import yaml
import smtplib
from email.mime.text import MIMEText
import tweepy

from database import Database

DATA_URL = ('https://data.montreal.ca/dataset/05a9e718-6810-4e73-8bb9-5955efeb91a0/resource/7f939a08-be8a-45e1-b208'
            '-d8744dca8fc6/download/violations.csv')
DATABASE = 'db/db.db'
EMAIL_CONFIG_FILE = 'config.yml'


def setup_twitter_api():
    client = tweepy.Client(
        consumer_key='ZkAhLcqVoFre266dmGIQdn5M2',
        consumer_secret='n3newK8MXEYsSRUXOEW9EObmyWzoCtqhOS25JWe69sgkfSJPlk',
        access_token='1776065910807105536-cwW15KepnFCI78r0MdreqqcKKwx4hn',
        access_token_secret='c51uc6QCDOxmJM3qrMzhcBnV9bYimgZPgPOGDE3gNVsKL',

    )

    return client


def post_to_twitter(establishment_names):
    client = setup_twitter_api()

    for name in establishment_names:
        tweet = f"New violation reported at {name} #ViolationAlert"
        try:
            client.create_tweet(text=tweet)
            print(f"Tweeted: {tweet}")
        except Exception as e:
            print(f"An error occurred: {e}")


def load_email_config():
    with open(EMAIL_CONFIG_FILE, 'r') as file:
        return yaml.safe_load(file)


def send_email(subject, body, config, recipient=None):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = config['sender']
    msg['To'] = recipient if recipient else config['recipient']

    with smtplib.SMTP(config['smtp_server'], config['smtp_port']) as server:
        server.ehlo()
        server.starttls()
        server.login(config['sender'], config['password'])
        server.send_message(msg)


def get_last_import_date(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(date) FROM violations")
    last_import_row = cursor.fetchone()
    return int(last_import_row[0]) if last_import_row and last_import_row[0] else 19700101


def detect_new_violations(reader, conn):
    last_import_date_int = get_last_import_date(conn)
    new_violations = []

    for row in reader:
        violation_date_int = int(row['date'])

        if violation_date_int > last_import_date_int:
            new_violations.append(row)

    return new_violations


def synchronize_data():
    config = load_email_config()

    response = requests.get(DATA_URL)
    response.raise_for_status()

    csv_data = csv.DictReader(response.text.splitlines())
    new_data = list(csv_data)

    with sqlite3.connect(DATABASE) as conn:
        new_violations = detect_new_violations(new_data, conn)
        if new_violations:
            cursor = conn.cursor()
            establishment_names = set()
            for row in new_violations:
                values = tuple(row[key] for key in csv_data.fieldnames)
                establishment_names.add(row['etablissement'])
                cursor.execute("""
                    INSERT INTO violations (
                        id_poursuite, business_id, date, description, adresse, date_jugement,
                        etablissement, montant, proprietaire, ville, statut, date_statut, categorie
                    ) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, values)
            conn.commit()

            email_body = "New violations detected:\n\n" + "\n".join(
                f"ID: {v['id_poursuite']}, Date: {v['date']}, Establishment: {v['etablissement']}" for v in
                new_violations
            )
            send_email("New Violations Detected", email_body, config)
            post_to_twitter(establishment_names)

            for name in establishment_names:
                emails = Database().get_user_emails_by_establishment_under_surveillance(name)
                email_body = "New violation detected at: {}".format(name)
                for email in emails:
                    send_email("New Violation Detected", email_body, config, email)

    print('Data synchronization complete.')
