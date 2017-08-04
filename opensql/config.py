"""Helper module for persisting settings in an SQLite DB"""
import os
import sqlite3
from appdirs import user_config_dir

APPNAME = 'opensql-pro'
CONFIG_DIR = user_config_dir(APPNAME)

os.makedirs(CONFIG_DIR, exist_ok=True)

CONFIG_DB = sqlite3.connect(CONFIG_DIR + '/config.db')
CONFIG_DB.row_factory = sqlite3.Row

def init():
    """Initialize configuration database"""
    cursor().execute('''CREATE TABLE IF NOT EXISTS connections
                        (id integer primary key,
                        name, host, port, user, pass)''')
    cursor().execute('''CREATE TABLE IF NOT EXISTS config
                        (id integer primary key, key, val)''')

def get_connections():
    """Get a list of all saved connections"""
    return cursor().execute('SELECT * FROM connections').fetchall()

def add_connection(name, host, port, user, password):
    """Add a new connection"""
    row = (name, host, port, user, password)
    cur = cursor()
    cur.execute('''INSERT INTO connections (name, host, port,user, pass)
                   VALUES(?,?,?,?,?)''', row)
    return cur.lastrowid

def get_connection(key):
    """Get a connection by id"""
    return cursor().execute('SELECT * FROM connections WHERE id = ?',
                            str(key)).fetchone()

def rm_connection(key):
    """Remove a connection by id"""
    cursor().execute('DELETE FROM connections WHERE id = ?', str(key))

def get_config(key, default=None):
    """Get a configuration value by key"""
    cur = cursor()
    cur.execute('SELECT val FROM config WHERE key = ?', [key])
    row = cur.fetchone()
    if row is None:
        return default
    return row[0]

def set_config(key, val):
    """Set a configuration value by key"""
    params = (key, str(val))
    cur = cursor()
    cur.execute('SELECT val FROM config WHERE key = ?', [key])
    row = cur.fetchone()
    print(params)
    if row is None:
        return cur.execute('INSERT INTO config (key, val) VALUES(?, ?)', params)
    return cur.execute('UPDATE config SET val = ? WHERE key = ?', params)

def cursor():
    """Get the database cursor instance"""
    return CONFIG_DB.cursor()

def commit():
    """Write changes to the database file"""
    return CONFIG_DB.commit()
