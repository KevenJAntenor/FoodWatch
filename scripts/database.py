import secrets
import sqlite3


class Database:
    def __init__(self, db_path='db/db.db'):
        self.db_path = db_path
        self.connection = None

    def get_connection(self):
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
        return self.connection

    def disconnect(self):
        if self.connection is not None:
            self.connection.close()
            self.connection = None

    def search_violations(self, search_by, search_term):
        valid_columns = ['etablissement', 'proprietaire', 'adresse']

        if search_by not in valid_columns:
            raise ValueError(f"Invalid search column: {search_by}")

        conn = self.get_connection()
        cur = conn.cursor()

        query = f"SELECT * FROM violations WHERE {search_by} LIKE ?"

        cur.execute(query, ('%' + search_term + '%',))
        rows = cur.fetchall()
        return rows

    def get_search_results_with_pagination(self, search_by, search_term, page, per_page=10):

        if search_by not in ['etablissement', 'proprietaire', 'adresse']:
            raise ValueError("Invalid search_by value")

        offset = (page - 1) * per_page
        conn = self.get_connection()
        cur = conn.cursor()

        cur.execute(f"SELECT COUNT(*) FROM violations WHERE {search_by} LIKE ?", ('%' + search_term + '%',))
        total_count = cur.fetchone()[0]

        cur.execute(f"SELECT * FROM violations WHERE {search_by} LIKE ? LIMIT ? OFFSET ?",
                    ('%' + search_term + '%', per_page, offset))
        rows = cur.fetchall()

        return rows, total_count

    def get_violations_between_dates(self, start_date, end_date):
        conn = self.get_connection()
        cursor = conn.cursor()

        start_date_int = int(start_date.replace('-', ''))
        end_date_int = int(end_date.replace('-', ''))

        query = """
        SELECT etablissement, COUNT(id_poursuite) as count
        FROM violations
        WHERE date BETWEEN ? AND ?
        GROUP BY etablissement
        """
        cursor.execute(query, (start_date_int, end_date_int))

        violations = cursor.fetchall()
        conn.close()
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in violations]

    def get_restaurant_names(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        query = "SELECT DISTINCT etablissement FROM violations ORDER BY etablissement"
        cursor.execute(query)

        names = [row['etablissement'] for row in cursor.fetchall()]
        conn.close()
        return names

    def get_infractions_by_restaurant(self, nom_restaurant):
        conn = self.get_connection()
        cursor = conn.cursor()

        query = """
        SELECT * FROM violations
        WHERE etablissement = ?
        """
        cursor.execute(query, (nom_restaurant,))

        infractions = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return infractions

    def get_establishments_with_infractions(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT etablissement, COUNT(*) as infraction_count
            FROM violations
            GROUP BY etablissement
            ORDER BY infraction_count DESC
        """)
        establishments = cursor.fetchall()
        result = [{"etablissement": row[0], "infraction_count": row[1]} for row in establishments]
        return result
        
    
    def insert_session(self, session_id, email):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO sessions (id_session, email) VALUES (?, ?)",
            (session_id, email),
        )
        conn.commit()


    def delete_session(self, session_id):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM sessions WHERE id_session = ?", (session_id,))
        conn.commit()

        conn.close()

    def get_user_id_by_session(self, session_id):
        conn = self.get_connection()
        cursor = conn.cursor()

        query = """
        SELECT utilisateur_id
        FROM sessions
        JOIN utilisateurs ON sessions.email = utilisateurs.email
        WHERE id_session = ?
        """
        cursor.execute(query, (session_id,))
        row = cursor.fetchone()
        
        user_id = row[0] if row else None

        conn.close()

        return user_id

    def get_user_by_email(self, email):
        conn = self.get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM utilisateurs WHERE email = ?"
        cursor.execute(query, (email,))
        user = cursor.fetchone()

        return user
    
    def get_user_by_id(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM utilisateurs WHERE utilisateur_id = ?"
        cursor.execute(query, (user_id,))
        user = cursor.fetchone()

        return user
    
    def get_user_profile_etablissements(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()

        query = "SELECT nom_etablissement FROM utilisateurs_etablissements WHERE utilisateur_id = ?"
        cursor.execute(query, (user_id,))
        rows = cursor.fetchall()

        etablissements = [row['nom_etablissement'] for row in rows]

        return etablissements

    def get_user_emails_and_tokens_by_establishment_under_surveillance(self, establishment_name):
        with self.connection.cursor() as cursor:
            cursor.execute("""
                SELECT u.email, u.token
                FROM utilisateurs u
                JOIN utilisateurs_etablissements ue ON u.utilisateur_id = ue.utilisateur_id
                WHERE ue.nom_etablissement = ?
            """, (establishment_name,))
            return cursor.fetchall()
        

    def insert_user(self, nom_complet, email, salt, hashed_password):
        conn = self.get_connection()
        cursor = conn.cursor()

        token = secrets.token_urlsafe(16)

        query = "INSERT INTO utilisateurs (nom_complet, email, hashed_password, salt, token) VALUES (?, ?, ?, ?, ?)"
        cursor.execute(query, (nom_complet, email, hashed_password, salt, token))
        conn.commit()

        user_id = cursor.lastrowid

        return user_id
    
    def insert_user_establishments(self, user_id, establishment_names):
        conn = self.get_connection()
        cursor = conn.cursor()

        for establishment_name in establishment_names:
            query = "INSERT INTO utilisateurs_etablissements (utilisateur_id, nom_etablissement) VALUES (?, ?)"
            cursor.execute(query, (user_id, establishment_name))

        conn.commit()

    def update_user_establishments(self, user_id, selectedEstablishments):
        conn = self.get_connection()
        cursor = conn.cursor()

        delete_query = """
            DELETE FROM utilisateurs_etablissements
            WHERE utilisateur_id = ?
        """
        cursor.execute(delete_query, (user_id,))

        for establishment in selectedEstablishments:
            insert_query = """
                INSERT OR IGNORE INTO utilisateurs_etablissements (utilisateur_id, nom_etablissement)
                VALUES (?, ?)
            """
            cursor.execute(insert_query, (user_id, establishment))

        conn.commit()


    def delete_establishment_from_user_establishments(self, token, establishment):
        conn = self.get_connection()
        cursor = conn.cursor()

        user_id_query = """
            SELECT utilisateur_id FROM utilisateurs WHERE token = ?
        """
        cursor.execute(user_id_query, (token,))
        user_id = cursor.fetchone()
        if user_id:
            user_id = user_id[0]  
        else:
            raise Exception("Token is incorrect or expired !")

        delete_query = """
            DELETE FROM utilisateurs_etablissements
            WHERE utilisateur_id = ?
            AND nom_etablissement = ?
        """
        cursor.execute(delete_query, (user_id, establishment))

        conn.commit()


    def update_user_photo_profile(self, user_id, photo_profil):
        conn = self.get_connection()
        cursor = conn.cursor()

        if photo_profil:
            photo_data = photo_profil.read()
            update_query = "UPDATE utilisateurs SET photo_profil = ? WHERE utilisateur_id = ?"
            cursor.execute(update_query, (photo_data, user_id))

        conn.commit()

    def insert_inspection_request(self, establishment, address, city, visit_date, last_name, first_name, description):
        conn = self.get_connection()
        cursor = conn.cursor()

        query = """
            INSERT INTO inspection_requests (nom_etablissement, adresse, ville, date_visite, nom_client, prenom_client, 
            description_probleme)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(query, (establishment, address, city, visit_date, last_name, first_name, description))
        conn.commit()

    def delete_etablissement(self, etablissement):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM inspection_requests WHERE etablissement = ?", (etablissement,))
        conn.commit()
        conn.close()

        return True 
    
    def update_etablissement_name(self, etablissement, new_etablissement):
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("UPDATE violations SET etablissement = ? WHERE etablissement = ?", (new_etablissement, etablissement))

            cursor.execute("UPDATE inspection_requests SET nom_etablissement = ? WHERE nom_etablissement = ?", (new_etablissement, etablissement))
            cursor.execute("UPDATE utilisateurs_etablissements SET nom_etablissement = ? WHERE nom_etablissement = ?", (new_etablissement, etablissement))

            conn.commit()
        finally:
            conn.close()


