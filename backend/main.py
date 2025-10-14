from fastapi import FastAPI, HTTPException, Depends, Response, Request # Inicializa o fastapi no main.py
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
import sqlite3 # Inicializa o sqlite3 no main.py
import bcrypt
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from pathlib import Path
import os

# Inicio ----------------------------------------------------------

env_path = Path(__file__).parent / ".env" # Manda procurar onde o arquivo .env esta e coloca o caminho na variavel
load_dotenv(dotenv_path=env_path) # Carrega a função que puxa as variaveis de ambiente do .env

app = FastAPI()

# ---- CORS -------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# FUNÇÃO QUE CONECTA O BANCO DE DADOS COM A API -------------------
def get_db_connection():
    conn = sqlite3.connect("./backend/users.db")
    conn.row_factory = sqlite3.Row
    return conn

# JSON WEB TOKEN --------------------------------------------------

SECRET_KEY = os.getenv("SECRET_KEY") # puxa a secret key do arquivo .env carregado pelo load_dotenv
ALGORITHM = os.getenv("ALGORITHM") # puxa o ALGORITHM do arquivo .env carregado pelo load_dotenv

def gerarToken(username: str, response: Response):
    payload = {
        "sub": username,
        "exp": datetime.now(timezone.utc) + timedelta(hours=1)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=3600
    )

    response.set_cookie(
        key="token_type",
        value="bearer",
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=3600
    )

    return token

def verificarToken(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Não autenticado")
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Token Invalido ou expirado!")

# -- Classes Pydantic ---------------------------------------------------------------------------------------------------
class UserRegister(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserReset(BaseModel):
    username: str
    new_password: str

#------------------------------------------------------------------------------------------------------------------------

@app.post("/register") # Cria a rota de registro
def register(user: UserRegister): # Define a função de registro com os paramentros usuario e senha em string
    conn = get_db_connection() # inicia a conexão com o banco de dados
    cursor = conn.cursor() # inicia o cursor (ponteiro que realmente executa os comandos SQL)

    if len(user.password) < 8: # Valida a senha somente se for maior que 8 caracteres
        raise HTTPException(status_code=400, detail="Senha deve ter no mínimo 8 caracteres.") # Caso não seja, exibe o erro 400

    password_bytes = user.password.encode('utf-8') # Transforma a senha digitada no registro em bytes
    salt = bcrypt.gensalt() # Gera a criptografia que sera usada no hash
    senhahash = bcrypt.hashpw(password_bytes, salt).decode('utf-8') # Transforma a senha digitada em senha com hash e transforma o hash em string 

    try: # Tenta executar
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (user.username, senhahash)) # Insere no banco de dados o usuario e senha criptografada
        conn.commit() # salva as alterações no banco de dados
        return {"message": f"Usuário {user.username} registrado com sucesso!"}
    except sqlite3.IntegrityError: # caso tenha um erro de integrity
        raise HTTPException(status_code=400, detail="Usuário já existe") # Mostra o erro 400
    
    finally:
        conn.close() # fecha conexão com o banco de dados


#------------------------------------------------------------------------------------------------------------------------

@app.post("/login") # Cria a rota de login
def login(user: UserLogin, response: Response): # função com entrada de parametro -> usuario e senha
    conn = get_db_connection() # inicia a conexão com o banco de dados
    cursor = conn.cursor() # inicia o cursor (ponteiro que realmente executa os comandos SQL)
    cursor.execute("SELECT password FROM users WHERE username = ?", (user.username,)) # executa o comando que seleciona o usuario e pega a senha salva desse usuario no DB
    row = cursor.fetchone() # Captura o retorno da execução do cursor

    if row is None: # se a linha for vazia
        raise HTTPException(status_code=401, detail="Credenciais Invalidas") # retorna erro de credencial
    else: # se não estiver vazia
        senhaUSER = row["password"] # pega a senha do username do banco de dados (este código com a chave "password" só funciona porque a saida é transformada em row na função get_connection_db())

    if bcrypt.checkpw(user.password.encode('utf-8'), senhaUSER.encode('utf-8')): # checagem da senha digitada no login com a senha real do usuario do banco de dados.
        token = gerarToken(user.username, response)
        return {"message": "Login foi feito! senha igual", "access_token": token, "token_type": "bearer"}

    else:
        raise HTTPException(status_code=401, detail="Credenciais Invalidas")

    ##### METODO ANTIGO - SEM CRIPTOGRAFIA BCRYPT
    # cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    # user = cursor.fetchone()

    # if user:
    #     return {"message": f"Usuario {username} logado com sucesso!"}
    # else:
    #     raise HTTPException(status_code=401, detail="Credenciais invalidas")

#------------------------------------------------------------------------------------------------------------------------
    
@app.post("/reset-password") # API pra resetar a senha
def resetsenha(user: UserReset): # entrada com nome de usuario e senha nova
    conn = get_db_connection() ## chama a conexão com o banco de dados
    cursor = conn.cursor() # inicia o cursor (ponteiro que realmente executa os comandos SQL)

    if len(user.new_password) < 8: # Valida a senha somente se for maior que 8 caracteres
        raise HTTPException(status_code=400, detail="Senha deve ter no mínimo 8 caracteres.") # Caso não seja, exibe o erro 400

    newPWBytes = user.new_password.encode('utf-8') ## transforma a senha da entrada do usuario em bytes

    salt = bcrypt.gensalt() # Gera o salt pra criptografia da senha 
    newPWHash = bcrypt.hashpw(newPWBytes, salt).decode('utf-8') # Transforma a senha do usuario em senha criptografada

    cursor.execute("UPDATE users SET password = ? WHERE username = ?", (newPWHash, user.username)) # Executa o comando SQL que atualiza a senha antiga pela senha nova, desde que exista o usuario da entrada

    if cursor.rowcount == 0: ## caso a linha retorne 0 
        raise HTTPException(status_code=404, detail="Usuário não encontrado") # exibe o erro
    
    conn.commit()  # commit do banco de dados, Aqui que realmente os dados são salvos no banco de dados (users.db)
    conn.close() # fecha a conexão com o banco de dados

    return {"message": f"Senha do usuario {user.username} resetada com sucesso!"} # Exibe a mensagem de sucesso
       

