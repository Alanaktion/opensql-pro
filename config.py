import sqlite3 # https://docs.python.org/2/library/sqlite3.html

configDb = sqlite3.connect('config.db')

def init():
    cursor().execute('''CREATE TABLE IF NOT EXISTS connections
                          (name, host, port, user, pass)''')

def get_connections():
	return cursor().execute('SELECT * FROM connections')

def add_connection(name, host, port, user, password):
	row = (name, host, port, user, password)
	cursor().execute('INSERT INTO connections VALUES(?,?,?,?,?)', row)

def cursor():
    global configDb
    return configDb.cursor()

def commit():
    global configDb
    configDb.commit()

# sampleConns = [
#     ('local', 'Local', 'localhost', 'root', 'letmein'),
#     ('test1', 'Test 1', 'test1.example.com', 'root', 'test'),
#     ('test2', 'Test 2', 'test2.example.com', 'example', 'hi'),
# ]
# c.executemany('INSERT INTO connections VALUES (?,?,?,?,?)', sampleConns)
# config.commit()
