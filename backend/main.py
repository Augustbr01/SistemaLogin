from fastapi import FastAPI, HTTPException # Inicializa o fastapi no main.py
import sqlite3 # Inicializa o sqlite3 no main.py
import bcrypt

app = FastAPI()

# FUNÇÃO QUE CONECTA O BANCO DE DADOS COM A API
def get_db_connection():
    conn = sqlite3.connect("./backend/users.db")
    conn.row_factory = sqlite3.Row
    return conn

#------------------------------------------------------------------------------------------------------------------------

@app.post("/register") # Cria a rota de registro
def register(username: str, password: str): # Define a função de registro com os paramentros usuario e senha em string
    conn = get_db_connection() # inicia a conexão com o banco de dados
    cursor = conn.cursor() # inicia o cursor (ponteiro que realmente executa os comandos SQL)

    if len(password) < 8: # Valida a senha somente se for maior que 8 caracteres
        raise HTTPException(status_code=400, detail="Senha deve ter no mínimo 8 caracteres.") # Caso não seja, exibe o erro 400

    password_bytes = password.encode('utf-8') # Transforma a senha digitada no registro em bytes

    salt = bcrypt.gensalt() # Gera a criptografia que sera usada no hash
    senhahash = bcrypt.hashpw(password_bytes, salt) # Transforma a senha digitada em senha com hash

    try: # Tenta executar
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, senhahash)) # Insere no banco de dados o usuario e senha criptografada
        conn.commit() # salva as alterações no banco de dados
        return {"message": f"Usuário {username} registrado com sucesso!"}
    except sqlite3.IntegrityError: # caso tenha um erro de integrity
        raise HTTPException(status_code=400, detail="Usuário já existe") # Mostra o erro 400
    
    finally:
        conn.close() # fecha conexão com o banco de dados


#------------------------------------------------------------------------------------------------------------------------

@app.post("/login") # Cria a rota de login
def login(username: str, password: str): # função com entrada de parametro -> usuario e senha
    conn = get_db_connection() # inicia a conexão com o banco de dados
    cursor = conn.cursor() # inicia o cursor (ponteiro que realmente executa os comandos SQL)

    cursor.execute("SELECT password FROM users WHERE username = ?", (username,)) # executa o comando que seleciona o usuario e pega a senha salva desse usuario no DB
    row = cursor.fetchone() # Captura o retorno da execução do cursor

    if row is None: # se a linha for vazia
        raise HTTPException(status_code=401, detail="Credenciais Invalidas") # retorna erro de credencial
    else: # se não estiver vazia
        senhaUSER = row["password"] # pega a senha do username do banco de dados (este código com a chave "password" só funciona porque a saida é transformada em row na função get_connection_db())

    password_bytes = password.encode('utf-8') # Transforma a senha digitada pelo usuario no login em bytes (sendo preparada para o check)

    if bcrypt.checkpw(password_bytes, senhaUSER): # checagem da senha digitada no login com a senha real do usuario do banco de dados.
        return {"message": "Login foi feito! senha igual"}
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
def resetsenha(username: str, new_password: str): # entrada com nome de usuario e senha nova
    conn = get_db_connection() ## chama a conexão com o banco de dados
    cursor = conn.cursor() # inicia o cursor (ponteiro que realmente executa os comandos SQL)

    if len(new_password) < 8: # Valida a senha somente se for maior que 8 caracteres
        raise HTTPException(status_code=400, detail="Senha deve ter no mínimo 8 caracteres.") # Caso não seja, exibe o erro 400

    newPWBytes = new_password.encode('utf-8') ## transforma a senha da entrada do usuario em bytes

    salt = bcrypt.gensalt() # Gera o salt pra criptografia da senha 
    newPWHash = bcrypt.hashpw(newPWBytes, salt) # Transforma a senha do usuario em senha criptografada

    cursor.execute("UPDATE users SET password = ? WHERE username = ?", (newPWHash, username)) # Executa o comando SQL que atualiza a senha antiga pela senha nova, desde que exista o usuario da entrada

    if cursor.rowcount == 0: ## caso a linha retorne 0 
        raise HTTPException(status_code=404, detail="Usuário não encontrado") # exibe o erro
    
    conn.commit()  # commit do banco de dados, Aqui que realmente os dados são salvos no banco de dados (users.db)
    conn.close() # fecha a conexão com o banco de dados

    return {"message": f"Senha do usuario {username} resetada com sucesso!"} # Exibe a mensagem de sucesso
       
    




