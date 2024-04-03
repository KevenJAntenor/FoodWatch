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
