# SistemaLogin — README (atualizado)

Este documento descreve o funcionamento das APIs e dos scripts Python do repositório, além de instruções para execução e pontos de segurança.

## Estrutura do projeto
- backend/main.py — API construída com FastAPI; autenticação com bcrypt + JWT; SQLite como armazenamento.
- backend/db_treino.py — script para criar o banco `users.db` e inserir um usuário de teste.
- Login/* — UI (HTML/JS/CSS) independente da API (pasta atualmente chamada "Login").
- .env — arquivo com variáveis de ambiente (não comitar).
- LICENSE, .gitignore, README.md

---

## Dependências principais (backend)
- fastapi
- uvicorn
- bcrypt
- python-jose[cryptography]
- python-dotenv
- pydantic
- sqlite3 (biblioteca padrão)

Instalação rápida:
```powershell
pip install fastapi uvicorn bcrypt python-jose[cryptography] python-dotenv pydantic
```

---

## backend/main.py — resumo do comportamento

Observação: o arquivo carrega variáveis do `.env` (via python-dotenv). Garanta um `.env` com pelo menos:
```
SECRET_KEY=uma_chave_secreta_aqui
ALGORITHM=HS256
```

1) Conexão com o banco
- Função: `get_db_connection()` abre `./backend/users.db` e define `row_factory = sqlite3.Row`.
- Responsabilidade de fechar a conexão: as rotas chamam `conn.close()` quando apropriado.

2) CORS
- Permitido apenas: http://127.0.0.1:5500 e http://localhost:5500 (útil para servir a pasta Login localmente).
- allow_credentials=True; allow_methods/headers = ["*"] (apenas para dev).

3) JWT
- `SECRET_KEY` e `ALGORITHM` são lidos do `.env`.
- `gerarToken(username, response)`:
  - Cria payload com `sub` (username) e `exp` (agora + 1 hora UTC).
  - Gera token JWT com jose.jwt.encode.
  - Seta cookies HTTP-only: `access_token` e `token_type` (secure=False em dev).
  - Retorna o token também no corpo da resposta.
- `verificarToken(request)`:
  - Lê cookie `access_token`; decodifica o JWT e valida expiração/assinatura.
  - Levanta 401 se ausente/inválido.

4) Modelos Pydantic
- UserRegister: username, password
- UserLogin: username, password
- UserReset: username, new_password

5) Endpoints (todos POST)

- POST /register
  - Entrada: JSON (UserRegister).
  - Validação: senha mínima 8 caracteres.
  - Processo:
    - gera salt + hash com bcrypt;
    - INSERT em users (username UNIQUE).
  - Erros:
    - 400 se username já existe (sqlite3.IntegrityError).
  - Resposta: mensagem de sucesso JSON.

- POST /login
  - Entrada: JSON (UserLogin).
  - Processo:
    - SELECT password FROM users WHERE username = ?;
    - compara com bcrypt.checkpw(password_plain, stored_hash).
    - se válido: chama gerarToken(...) para setar cookies e retorna token no corpo.
  - Erros:
    - 401 se usuário não encontrado ou credenciais inválidas.

- POST /reset-password
  - Entrada: JSON (UserReset).
  - Validação: new_password mínimo 8 caracteres.
  - Processo:
    - gera novo hash com bcrypt;
    - UPDATE users SET password = ? WHERE username = ?;
    - se cursor.rowcount == 0: retorna 404 (usuário não encontrado).
    - commit e retorna sucesso.
  - Observação: fecha a conexão.

---

## backend/db_treino.py
- Cria tabela `users` se não existir:
  - id INTEGER PRIMARY KEY AUTOINCREMENT
  - username TEXT UNIQUE NOT NULL
  - password TEXT NOT NULL
- Insere um usuário de teste (script atual insere um exemplo; recomenda-se inserir com senha já hasheada).
- Uso:
```powershell
python backend/db_treino.py
```

---

## UI (pasta Login)
- Arquivos principais:
  - Login/index.html
  - Login/index.js
  - Login/style.css
- Observação: a pasta se chama `Login/` (corrigido). É uma UI estática; para testar localmente:
```powershell
cd Login
python -m http.server 5500
```
Abra http://127.0.0.1:5500 no navegador. Ajuste CORS no backend se front e backend estiverem em origens diferentes (o main.py já permite as origens de exemplo).

---

## Exemplos de uso (curl) — JSON

Registrar:
```bash
curl -X POST "http://127.0.0.1:8000/register" \
  -H "Content-Type: application/json" \
  -d '{"username":"novo","password":"senha12345"}'
```

Login (salva cookies):
```bash
curl -X POST "http://127.0.0.1:8000/login" \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{"username":"novo","password":"senha12345"}'
```
- O cookie `access_token` será salvo em cookies.txt; o token também é retornado no corpo.

Resetar senha:
```bash
curl -X POST "http://127.0.0.1:8000/reset-password" \
  -H "Content-Type: application/json" \
  -d '{"username":"novo","new_password":"novaSenha123"}'
```

---

## Como rodar (desenvolvimento)
1. Criar arquivo .env com SECRET_KEY e ALGORITHM.
2. Criar banco:
```powershell
python backend/db_treino.py
```
3. Rodar API:
```powershell
uvicorn backend.main:app --reload
```
4. Servir frontend:
```powershell
cd Login
python -m http.server 5500
```

---

## Pontos de segurança e melhorias recomendadas (prioridade)
1. Não comitar `.env` nem `SECRET_KEY`. Use variáveis de ambiente em produção.
2. Em produção:
   - HTTPS (cookies `secure=True`), definir SameSite adequado e considerar proteção CSRF.
   - Rotação de chaves/refresh tokens e políticas de expiração mais robustas.
   - Rate limiting / proteção contra brute force.
3. Banco:
   - SQLite é adequado para dev; para produção, usar Postgres ou similar com pool de conexões.
4. Senhas:
   - O código já usa bcrypt — manter parametros de custo adequados.
   - db_treino.py deve inserir hashes, nunca senhas em texto.
5. Validações:
   - Normalizar/limitar usernames, logs cuidadosos (nunca logar senhas).
6. Possível evolução:
   - Usar ORM (SQLAlchemy), testes automatizados, rotas protegidas com dependências FastAPI que usam `verificarToken`.

---

## Referências rápidas (onde olhar no código)
- backend/main.py — get_db_connection, gerarToken, verificarToken, modelos Pydantic e endpoints.
- backend/db_treino.py — script de criação/seed do banco.
- Login/ — frontend estático.
- .env — variáveis de configuração.