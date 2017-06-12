"""Helper module for persisting settings in an SQLite DB"""
import sqlite3 # https://docs.python.org/2/library/sqlite3.html

config_db = sqlite3.connect('config.db')

def init():
    """Initialize configuration database"""
    cursor().execute('''CREATE TABLE IF NOT EXISTS connections
                        (name, host, port, user, pass)''')

def get_connections():
    """Get a list of all saved connections"""
    return cursor().execute('SELECT * FROM connections').fetchall()

def add_connection(name, host, port, user, password):
    """Add a new connection"""
    row = (name, host, port, user, password)
    cursor().execute('INSERT INTO connections VALUES(?,?,?,?,?)', row)

def get_connection(name):
    """Get a connection by name"""
    cursor().execute('SELECT * FROM connections WHERE name = ?',
                     name).fetchone()

def rm_connection(name):
    """Remove a connection by name"""
    cursor().execute('DELETE FROM connections WHERE name = ?', name)

def cursor():
    """Get the database cursor instance"""
    global config_db
    return config_db.cursor()

def commit():
    """Write changes to the database file"""
    global config_db
    return config_db.commit()
