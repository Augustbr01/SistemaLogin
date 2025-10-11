# SistemaLogin — README

Este arquivo documenta como funcionam as APIs e os scripts Python no repositório.

## Visão geral dos arquivos
- [backend/main.py](backend/main.py) — implementação da API com FastAPI e SQLite.
- [backend/db_treino.py](backend/db_treino.py) — script de criação da base `users.db` e inserção de um usuário de teste.
- [frontend/index.html](frontend/index.html) — UI (HTML).
- [frontend/index.js](frontend/index.js) — scripts da UI (troca entre login / register).
- [frontend/style.css](frontend/style.css) — estilos.
- [LICENSE](LICENSE)
- [.gitignore](.gitignore)
- [README.md](README.md)

## Backend (Python)

Os arquivos Python estão em [backend/](backend). Explanação dos elementos principais em [backend/main.py](backend/main.py):

### Conexão com o banco
- Função: [`main.get_db_connection`](backend/main.py)  
  - Abre conexão SQLite com o arquivo `users.db`.
  - Define `row_factory = sqlite3.Row` para permitir acesso por nome de coluna.
  - Retorna um objeto `sqlite3.Connection`.

### Endpoints (FastAPI)
Todos os endpoints são métodos POST definidos em [backend/main.py](backend/main.py):

1. [`main.register`](backend/main.py) — POST /register  
   - Parâmetros esperados: `username: str`, `password: str` (são recebidos como campos do corpo/form).  
   - Ação: insere na tabela `users` um novo registro `(username, password)`.  
   - Resposta: JSON com mensagem de sucesso.  
   - Erros: se `username` já existir, dispara `sqlite3.IntegrityError` e retorna `HTTPException(status_code=400, detail="Usuário já existe")`.  
   - Observação de segurança: a senha é guardada em texto simples (inseguro).

2. [`main.login`](backend/main.py) — POST /login  
   - Parâmetros: `username: str`, `password: str`.  
   - Ação: faz SELECT na tabela `users` com `WHERE username = ? AND password = ?`.  
   - Resposta: se houver correspondência, retorna mensagem de sucesso; caso contrário, retorna `HTTPException(status_code=401, detail="Credenciais invalidas")`.  
   - Observação: autenticação baseada em comparação direta de texto da senha.

3. [`main.resetsenha`](backend/main.py) — POST /reset-password  
   - Parâmetros: `username: str`, `new_password: str`.  
   - Ação: executa `UPDATE users SET password = ? WHERE username = ?`.  
   - Resposta: mensagem de sucesso.  
   - Erro tratado (incorreto): código tenta capturar `sqlite3.IntegrityError` para usuário não encontrado, mas `UPDATE` que não altera linhas não gera `IntegrityError`. Atualmente não há verificação se o usuário realmente existia antes do commit.  
   - Observação de segurança: mesma questão de senha em texto simples.

### Script de criação do banco
- [backend/db_treino.py](backend/db_treino.py)  
  - Cria tabela `users` se não existir:
    - id INTEGER PRIMARY KEY AUTOINCREMENT
    - username TEXT UNIQUE NOT NULL
    - password TEXT NOT NULL
  - Insere um usuário de teste: `("augusto", "1234")`
  - Fecha a conexão.

## Exemplos de uso (curl)

- Registrar:
```bash
curl -X POST "http://127.0.0.1:8000/register" -F "username=novo" -F "password=senha123"
```

- Login:
```bash
curl -X POST "http://127.0.0.1:8000/login" -F "username=novo" -F "password=senha123"
```

- Resetar senha:
```bash
curl -X POST "http://127.0.0.1:8000/reset-password" -F "username=novo" -F "new_password=senhaNova"
```

## Pontos importantes / melhorias recomendadas
1. Senhas:
   - Não salvar senhas em texto plano. Usar hashing forte (bcrypt / argon2).  
   - Exemplo: hash antes do INSERT; na autenticação, comparar hash.
2. Validação e parsing:
   - Usar modelos Pydantic para definir e validar payloads (por exemplo `BaseModel` com campos `username` e `password`).
3. Respostas e erros:
   - Em `/reset-password`, verificar número de linhas afetadas por `cursor.rowcount` (ou fazer um SELECT antes) para retornar 404 se o usuário não existir.
4. Injeção e SQL:
   - O código atual usa parâmetros `?`, o que evita injeção quando usado corretamente (bom). Manter sempre parâmetros parametrizados.
5. Conexão com DB:
   - Em ambientes concorrentes (FastAPI + Uvicorn) o uso direto de sqlite3 pode causar bloqueios; considerar usar pool ou banco adequado (Postgres) se for produzir.
6. Segurança geral:
   - Usar HTTPS em produção.
   - Implementar mecanismos de rate limiting e proteção contra brute-force.

## Frontend
- A UI simples está em [frontend/index.html](frontend/index.html), [frontend/index.js](frontend/index.js) e [frontend/style.css](frontend/style.css).
- O frontend atual não está integrado com a API (os formulários não fazem requisições HTTP); é apenas a interface visual e troca entre telas de login/register.

## Como iniciar
1. Criar o banco (executar o script de treino):
```bash
python backend/db_treino.py
```
2. Rodar a API:
```bash
uvicorn backend.main:app --reload
```
3. Abrir a UI em um servidor estático apontando `frontend/index.html` (por exemplo abrir no navegador ou usar um simples `python -m http.server` na pasta `frontend`), lembrando de configurar CORS na API se for testar cross-origin.

---

Referências aos símbolos no código:
- [`main.get_db_connection`](backend/main.py)  
- [`main.register`](backend/main.py)  
- [`main.login`](backend/main.py)  
- [`main.resetsenha`](backend/main.py)  
- [backend/db_treino.py](backend/db_treino.py)