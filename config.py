"""Helper module for persisting settings in an SQLite DB"""
import os
import sqlite3 # https://docs.python.org/2/library/sqlite3.html
from appdirs import user_config_dir

appname = 'opensql-pro'
config_dir = user_config_dir(appname)

os.makedirs(config_dir, exist_ok=True)

config_db = sqlite3.connect(config_dir + '/config.db')
config_db.row_factory = sqlite3.Row

def init():
    """Initialize configuration database"""
    cursor().execute('''CREATE TABLE IF NOT EXISTS connections
                        (id integer primary key,
                        name, host, port, user, pass)''')

def get_connections():
    """Get a list of all saved connections"""
    return cursor().execute('SELECT * FROM connections').fetchall()

def add_connection(name, host, port, user, password):
    """Add a new connection"""
    row = (name, host, port, user, password)
    cursor().execute('''INSERT INTO connections (name, host, port,user, pass)
                        VALUES(?,?,?,?,?)''', row)

def get_connection(key):
    """Get a connection by id"""
    return cursor().execute('SELECT * FROM connections WHERE id = ?',
                            str(key)).fetchone()

def rm_connection(key):
    """Remove a connection by id"""
    cursor().execute('DELETE FROM connections WHERE id = ?', str(key))

def cursor():
    """Get the database cursor instance"""
    global config_db
    return config_db.cursor()

def commit():
    """Write changes to the database file"""
    global config_db
    return config_db.commit()
