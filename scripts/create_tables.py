import sqlite3

class Database:
    def __init__(self):
        self.connection = sqlite3.connect('db/db.db')
        self.cursor = self.connection.cursor()

    def get_connection(self):
        return self.connection

    def execute_script(self, script_file):
        with open(script_file, 'r') as file:
            script = file.read()
            self.cursor.executescript(script)
            self.connection.commit()

    def close(self):
        self.connection.close()

if __name__ == '__main__':
    db = Database()
    db.execute_script('db/db.sql') 
    db.close()
