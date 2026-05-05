# Estrutura do Projeto (src)

### Nome da API e Descrição Geral
**Notas Fiscais Python** — API para gerenciamento de notas fiscais.

Este documento explica a responsabilidade de cada diretório dentro do `src/`, ajudando a manter o código organizado e prático.

## Diretórios e Arquivos

- **`main.py`**: Ponto de entrada (entrypoint) da aplicação. Responsável por inicializar o servidor/aplicativo, criar conexões de banco e registrar as rotas.

- **`actions/`**: Ações específicas e fluxos de negócio do sistema. Estas funções/classes processam lógicas orquestrando processos e fazendo a ponte com serviços ou banco de dados.

- **`dtos/`**: Data Transfer Objects (Objetos de Transferência de Dados). Usados para definir esquemas e validação de dados de entrada/saída (ex: Modelos Pydantic) e trafegar informações entre as pastas da aplicação.

- **`entities/`**: Modelos do banco de dados (ORM). Representam de fato as tabelas e o esquema relacional, contendo as entidades mapeadas no SQLAlchemy.

- **`repositories/`**: Camada de acesso a dados. Abstrai a comunicação com o banco de dados ou outras fontes de dados estáticas/externas, provendo uma interface limpa para que o restante do sistema pesquise ou salve as entidades.

- **`routes/`**: Controladores de entrega (Endpoints/Controllers). Responsável por lidar com requisições HTTP, processar dados de entrada (payload/query params) e repassar a execução para a camada de `actions`.

- **`services/`**: Lógica de integração e regras de domínio ou infraestrutura mais amplas. Geralmente lidam com chamadas a APIs externas (ex: API da SEFAZ, sistemas de terceiros), rotinas em background ou lógicas mais generalistas que dão suporte aos `actions`.

### Principais Endpoints
Todos os endpoints estão versionados sob o prefixo `/api/v1`:

- `GET /api/v1/users` — Listar todos os usuários
- `GET /api/v1/users/{user_id}` — Buscar um usuário pelo ID
- `POST /api/v1/users` — Criar um novo usuário
- `PUT /api/v1/users/{user_id}` — Atualizar um usuário existente
- `DELETE /api/v1/users/{user_id}` — Remover um usuário (soft delete)

### Estrutura dos Dados
**Usuário (UserModel):**
- `id` (int) — Identificador único, gerado automaticamente
- `name` (str) — Nome do usuário
- `email` (str) — E-mail único do usuário
- `password` (str) — Senha do usuário (armazenada com hash bcrypt)
- `created_at` (datetime) — Data de criação
- `updated_at` (datetime) — Data da última atualização
- `deleted_at` (datetime | None) — Data de exclusão (soft delete)

### Ferramentas e Tecnologias
- **Linguagem:** Python 3.13+
- **Framework Web:** FastAPI
- **ORM:** SQLAlchemy (asyncio) com Alembic para migrações
- **Banco de Dados:** PostgreSQL (via psycopg)
- **Validação:** Pydantic + pydantic-settings
- **Hashing de Senha:** bcrypt
- **Scraping:** BeautifulSoup4 + HTTPX
- **Linter/Formatter:** Ruff
- **Containerização:** Docker + Docker Compose
- **Formato de Dados:** JSON