import sqlite3 # https://docs.python.org/2/library/sqlite3.html

configDb = sqlite3.connect('config.db')

def init():
    global configDb
    c = configDb.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS connections
                (name, label, host, user, pass)''')

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
