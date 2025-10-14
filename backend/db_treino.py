import sqlite3

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    number INTEGER UNIQUE NOT NULL
)
''')

cursor.execute('INSERT INTO users (email, username, password, number) VALUES (?, ?, ?, ?)', ("teste@teste.com", "teste", "teste2025", "55679855925152"))

conn.commit()
conn.close()

print("Banco criado e usuário inserido com sucesso!")