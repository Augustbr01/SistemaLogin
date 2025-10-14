# SistemaLogin — README (atualizado)

Documento explicativo das APIs e dos scripts Python presentes no repositório.

## Estrutura do projeto
- backend/main.py — API construída com FastAPI; autenticação com bcrypt + JWT; SQLite como armazenamento.
- backend/db_treino.py — script para criar o banco `users.db` e inserir um usuário de teste.
- frontend/* — UI (HTML/JS/CSS) independente da API.
- LICENSE, .gitignore, README.md

---

## Dependências principais (backend)
- fastapi
- uvicorn
- bcrypt
- python-jose
- pydantic
- sqlite3 (biblioteca padrão)

Instalação rápida:
```bash
pip install fastapi uvicorn bcrypt python-jose[cryptography] pydantic
```

---

## backend/main.py — visão completa

### Conexão com o banco
Função: `get_db_connection()`
- Abre `sqlite3.connect("./backend/users.db")`.
- Define `conn.row_factory = sqlite3.Row` para permitir acesso por nome de coluna.
- Retorna uma conexão SQLite. Fechar a conexão após uso é responsabilidade do código que a chamou.

### Configuração de CORS
- Middleware CORS configurado para permitir origens:
  - http://127.0.0.1:5500
  - http://localhost:5500
- Métodos e headers permitidos são liberais (`allow_methods=["*"]`, `allow_headers=["*"]`) — aceitável para desenvolvimento, inseguro para produção.

### JWT (JSON Web Token)
- Constantes:
  - `SECRET_KEY = "IEJWIJFANzCX"` (chave fixa — só para dev; em produção usar variável de ambiente)
  - `ALGORITHM = "HS256"`
- `gerarToken(username: str, response: Response)`:
  - Cria payload com `sub` (subject = username) e `exp` (expiração = agora + 1 hora UTC).
  - Gera token via `jose.jwt.encode`.
  - Define cookies HTTP-only:
    - `access_token` com o token (httponly, secure=False — dev, samesite=lax, max_age=3600).
    - `token_type` = "bearer".
  - Retorna o token (também incluído no corpo da resposta atualmente).
- `verificarToken(request: Request)`:
  - Lê cookie `access_token`. Se ausente -> 401.
  - Decodifica/valida token; se inválido/expirado -> 401.
  - Retorna o payload decodificado (útil como dependência para proteger rotas).

> Observação: `secure=False` e chave fixa são aceitáveis apenas em ambiente de desenvolvimento. Em produção usar HTTPS e variáveis de ambiente.

### Modelos Pydantic
- `UserRegister` — campos: `username: str`, `password: str`
- `UserLogin` — campos: `username: str`, `password: str`
- `UserReset` — campos: `username: str`, `new_password: str`

### Endpoints (todos `POST`)

1) POST /register
- Entrada: JSON com `username` e `password` (Pydantic `UserRegister`).
- Valida: senha mínima 8 caracteres.
- Gera salt + hash com `bcrypt` e armazena `senhahash` na tabela `users`.
- Trava de unicidade em `username` -> captura `sqlite3.IntegrityError` e retorna 400 se já existir.
- Retorna JSON de confirmação.
- Observação: senha é armazenada como hash `bcrypt` (boa prática).

2) POST /login
- Entrada: JSON com `username` e `password` (`UserLogin`).
- Seleciona `password` (hash) do usuário no DB.
- Se usuário não existir -> 401.
- Usa `bcrypt.checkpw(entered_password, stored_hash)` para validar.
- Se válido:
  - Gera JWT com `gerarToken(...)`, define cookies e retorna JSON contendo `access_token` e `token_type`.
- Se inválido -> 401.

3) POST /reset-password
- Entrada: JSON com `username` e `new_password` (`UserReset`).
- Valida: senha mínima 8 caracteres.
- Gera novo hash com `bcrypt` e executa:
  - `UPDATE users SET password = ? WHERE username = ?`
- Verifica `cursor.rowcount`:
  - Se 0 -> 404 (usuário não encontrado).
  - Senao -> commit e resposta de sucesso.
- Fecha conexão.

### Observações sobre concorrência / SQLite
- SQLite funciona para desenvolvimento. Em ambiente com múltiplos workers/threads/requests simultâneos prefira um banco com conexão concorrente (Postgres) ou use um gerenciador de conexões apropriado.

---

## backend/db_treino.py
- Cria tabela `users` se não existir:
  - id INTEGER PRIMARY KEY AUTOINCREMENT
  - username TEXT UNIQUE NOT NULL
  - password TEXT NOT NULL
- Insere um usuário de teste (ex.: `("augusto","1234")`) — idealmente, nesse script a senha deveria já vir hasheada (atualmente pode inserir texto puro; ajuste recomendado).
- Uso:
```bash
python backend/db_treino.py
```

---

## Exemplos de uso (curl) — agora usando JSON
Registrar:
```bash
curl -X POST "http://127.0.0.1:8000/register" \
  -H "Content-Type: application/json" \
  -d '{"username":"novo","password":"senha12345"}'
```

Login (recebe cookie e token no corpo):
```bash
curl -X POST "http://127.0.0.1:8000/login" \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{"username":"novo","password":"senha12345"}'
```
- `-c cookies.txt` salva cookies retornados (útil para requests subsequentes que dependam do cookie).

Resetar senha:
```bash
curl -X POST "http://127.0.0.1:8000/reset-password" \
  -H "Content-Type: application/json" \
  -d '{"username":"novo","new_password":"novaSenha123"}'
```

---

## Como rodar (desenvolvimento)
1. Criar banco:
```bash
python backend/db_treino.py
```
2. Rodar API:
```bash
uvicorn backend.main:app --reload
```
3. Frontend: servir `frontend/` via servidor estático (ex.: `python -m http.server` dentro da pasta `frontend`) ou abrir arquivos diretamente no navegador. Se front e backend estiverem em origens diferentes, ajustar CORS.

---

## Pontos de segurança / melhorias recomendadas
- Nunca comitar `SECRET_KEY` em código. Usar variáveis de ambiente (ex.: `os.environ`).
- Em produção:
  - usar HTTPS (cookies `secure=True`);
  - definir SameSite apropriado e considerar CSRF;
  - usar longas chaves secretas e rotação periódica;
  - considerar expirar/renovar refresh tokens (fluxo de refresh tokens);
  - aplicar políticas de rate limiting/brute-force protection.
- db_treino.py: inserir senhas já hasheadas ou mudar script.
- Validar/normalizar usernames (trim, tamanho máximo, caracteres permitidos).
- Registrar logs de tentativas falhas (com cuidado para não logar senhas).
- Considerar uso de ORMs (SQLAlchemy) e conexão gerenciada para maior robustez.

---

## Referências (símbolos no código)
- `get_db_connection` — abre conexão SQLite.
- `gerarToken` — cria JWT e seta cookies.
- `verificarToken` — valida token a partir do cookie.
- `UserRegister`, `UserLogin`, `UserReset` — modelos Pydantic.
- Endpoints: `/register`, `/login`, `/reset-password`.