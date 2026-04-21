# Estrutura do Projeto (src)

Este documento explica a responsabilidade de cada diretório dentro do `src/`, ajudando a manter o código organizado e prático.

## Diretórios e Arquivos

- **`main.py`**: Ponto de entrada (entrypoint) da aplicação. Responsável por inicializar o servidor/aplicativo, criar conexões de banco e registrar as rotas.

- **`actions/`**: Ações específicas e fluxos de negócio do sistema. Estas funções/classes processam lógicas orquestrando processos e fazendo a ponte com serviços ou banco de dados.

- **`dtos/`**: Data Transfer Objects (Objetos de Transferência de Dados). Usados para definir esquemas e validação de dados de entrada/saída (ex: Modelos Pydantic) e trafegar informações entre as pastas da aplicação.

- **`entities/`**: Modelos do banco de dados (ORM). Representam de fato as tabelas e o esquema relacional, contendo as entidades mapeadas no SQLAlchemy.

- **`repositories/`**: Camada de acesso a dados. Abstrai a comunicação com o banco de dados ou outras fontes de dados estáticas/externas, provendo uma interface limpa para que o restante do sistema pesquise ou salve as entidades.

- **`routes/`**: Controladores de entrega (Endpoints/Controllers). Responsável por lidar com requisições HTTP, processar dados de entrada (payload/query params) e repassar a execução para a camada de `actions`.

- **`services/`**: Lógica de integração e regras de domínio ou infraestrutura mais amplas. Geralmente lidam com chamadas a APIs externas (ex: API da SEFAZ, sistemas de terceiros), rotinas em background ou lógicas mais generalistas que dão suporte aos `actions`.
