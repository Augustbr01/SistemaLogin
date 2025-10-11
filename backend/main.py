from fastapi import FastAPI, HTTPException # Inicializa o fastapi no main.py
import sqlite3 # Inicializa o sqlite3 no main.py

app = FastAPI()

# FUNÇÃO QUE CONECTA O BANCO DE DADOS COM A API
def get_db_connection():
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.post("/register")
def register(username: str, password: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password)
        )
        conn.commit()
        return {"message": f"Usuário {username} registrado com sucesso!"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Usuário já existe")
    
    finally:
        conn.close()

@app.post("/login")
def login(username: str, password: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()

    if user:
        return {"message": f"Usuario {username} logado com sucesso!"}
    else:
        raise HTTPException(status_code=401, detail="Credenciais invalidas")
    
@app.post("/reset-password")
def resetsenha(username: str, new_password: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    
    status = cursor.fetchone()


    try:
        cursor.execute("UPDATE users SET password = ? WHERE username = ?", (new_password, username))
        conn.commit()
        return {"message": f"Senha do usuario {username} resetada com sucesso!"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    finally:
        conn.close()




