# Documentação — Integração NFC-e Scraper com FastAPI

# Visão Geral

Este documento descreve toda a implementação do módulo de scraping de NFC-e integrado ao backend FastAPI do projeto `notas-fiscais-python`.

O objetivo do módulo é:

- Receber uma URL de NFC-e
- Fazer requisição HTTP para a SEFAZ
- Baixar o HTML da nota fiscal
- Extrair os dados relevantes utilizando BeautifulSoup
- Retornar um JSON estruturado via endpoint FastAPI

---

# Fluxo Geral da Aplicação

```text
Cliente
   ↓
POST /v1/nfce/parse
   ↓
FastAPI Route
   ↓
NFCe Service
   ↓
HTTPX Fetcher
   ↓
SEFAZ NFC-e
   ↓
HTML Response
   ↓
BeautifulSoup Parser
   ↓
Extractor
   ↓
JSON Estruturado
   ↓
Response API
```

---

# Tecnologias Utilizadas

| Tecnologia     | Função                          |
| -------------- | ------------------------------- |
| FastAPI        | Framework da API                |
| HTTPX          | Requisições HTTP assíncronas    |
| BeautifulSoup4 | Parsing HTML                    |
| lxml           | Parser HTML de alta performance |
| Pydantic       | Validação e serialização        |
| Uvicorn        | Servidor ASGI                   |

---

# Estrutura Criada

```text
src/
├── dtos/
│   └── nfce_dtos.py
│
├── routes/
│   └── v1/
│       └── nfce_routes.py
│
├── services/
│   └── nfce/
│       ├── __init__.py
│       ├── fetcher.py
│       ├── parser.py
│       ├── extractor.py
│       ├── helpers.py
│       └── nfce_service.py
```

---

# Arquitetura Utilizada

A implementação seguiu o padrão arquitetural já existente no projeto.

## Separação de responsabilidades

| Camada    | Responsabilidade                 |
| --------- | -------------------------------- |
| routes    | Receber requisições HTTP         |
| dtos      | Validar dados de entrada e saída |
| services  | Regras de negócio e integrações  |
| fetcher   | Comunicação HTTP externa         |
| parser    | Criação do BeautifulSoup         |
| extractor | Extração dos dados do HTML       |
| helpers   | Funções utilitárias              |

---

# Explicação Completa dos Arquivos

# 1. helpers.py

## Objetivo

Responsável por funções auxiliares reutilizáveis.

## Código

```python
# src/services/nfce/helpers.py

def clean_text(value, remove_text: str = ''):
    if not value:
        return None

    text = value.get_text(strip=True)

    if remove_text:
        text = text.replace(remove_text, '')

    return text.strip()


def to_float(value: str | None):
    if not value:
        return None

    value = value.replace('.', '')
    value = value.replace(',', '.')

    try:
        return float(value)
    except ValueError:
        return None
```

---

## O que o clean_text faz?

Essa função:

- Remove espaços extras
- Remove labels desnecessárias
- Limpa texto HTML

### Exemplo

Entrada:

```text
Qtde.:0,368
```

Saída:

```text
0,368
```

---

## O que o to_float faz?

Converte números brasileiros:

```text
13,98
```

para:

```python
13.98
```

Isso é necessário para retornar valores numéricos válidos no JSON.

---

# 2. fetcher.py

## Objetivo

Responsável por:

- Fazer requisições HTTP
- Buscar o HTML da NFC-e
- Simular um navegador real

## Código

```python
# src/services/nfce/fetcher.py

import httpx


async def fetch_page(url: str) -> str:
    headers = {
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/124.0.0.0 Safari/537.36'
        )
    }

    async with httpx.AsyncClient(
        timeout=30,
        follow_redirects=True,
    ) as client:

        response = await client.get(
            url,
            headers=headers,
        )

        response.raise_for_status()

        return response.text
```

---

## Por que HTTPX?

HTTPX foi utilizado porque:

- suporta async/await
- integra melhor com FastAPI
- possui melhor arquitetura moderna
- é compatível com aplicações ASGI

---

## Por que usar User-Agent?

Muitos sites da SEFAZ bloqueiam requisições sem User-Agent.

O header faz a requisição parecer um navegador real.

---

# 3. parser.py

## Objetivo

Transformar o HTML bruto em um objeto navegável BeautifulSoup.

## Código

```python
# src/services/nfce/parser.py

from bs4 import BeautifulSoup


def parse_html(html: str):
    return BeautifulSoup(html, 'lxml')
```

---

## O que o BeautifulSoup faz?

BeautifulSoup converte HTML em uma árvore DOM navegável.

Isso permite:

- localizar elementos
- buscar classes CSS
- navegar entre tags
- extrair textos

---

## Por que usar lxml?

O parser `lxml` é:

- mais rápido
- mais robusto
- melhor para HTML complexo

---

# 4. extractor.py

## Objetivo

Responsável por:

- localizar elementos HTML
- extrair informações
- estruturar dados

## Código

```python
# src/services/nfce/extractor.py

from src.services.nfce.helpers import clean_text, to_float


def extract_store(soup):
    return {
        'name': clean_text(
            soup.find(class_='txtTopo')
        )
    }



def extract_items(soup):
    items = []

    products = soup.find_all('tr')

    for product in products:

        name = product.find(class_='txtTit2')

        if not name:
            continue

        code = clean_text(
            product.find(class_='RCod'),
            '(Código:'
        )

        if code:
            code = code.replace(')', '').strip()

        quantity = clean_text(
            product.find(class_='Rqtd'),
            'Qtde.:'
        )

        unit = clean_text(
            product.find(class_='RUN'),
            'UN:'
        )

        unit_price = clean_text(
            product.find(class_='RvlUnit'),
            'Vl. Unit.:'
        )

        total_price = clean_text(
            product.find(class_='valor')
        )

        item = {
            'name': clean_text(name),
            'code': code,
            'quantity': to_float(quantity),
            'unit': unit,
            'unit_price': to_float(unit_price),
            'total_price': to_float(total_price),
        }

        items.append(item)

    return items



def extract_total(soup):
    total = clean_text(
        soup.find(class_='txtMax')
    )

    return to_float(total)
```

---

## Como funciona a extração?

O extractor utiliza:

```python
soup.find()
```

para encontrar elementos específicos.

### Exemplo

```python
soup.find(class_='txtTopo')
```

Busca:

```html
<div class="txtTopo"></div>
```

---

# 5. nfce_service.py

## Objetivo

Orquestrar todo o processo.

## Código

```python
# src/services/nfce/nfce_service.py

from src.services.nfce.extractor import (
    extract_items,
    extract_store,
    extract_total,
)
from src.services.nfce.fetcher import fetch_page
from src.services.nfce.parser import parse_html


async def parse_nfce(url: str):
    html = await fetch_page(url)

    soup = parse_html(html)

    return {
        'store': extract_store(soup),
        'items': extract_items(soup),
        'total': extract_total(soup),
    }
```

---

## Responsabilidade do Service

O service:

- chama o fetcher
- chama o parser
- chama os extractors
- organiza o retorno final

---

# 6. DTOs

## Objetivo

Definir:

- estrutura do request
- estrutura da response
- validação automática
- documentação Swagger

## Código

```python
# src/dtos/nfce_dtos.py

from pydantic import BaseModel


class NFCeParseRequest(BaseModel):
    url: str


class NFCeStore(BaseModel):
    name: str


class NFCeItem(BaseModel):
    name: str
    code: str | None
    quantity: float | None
    unit: str | None
    unit_price: float | None
    total_price: float | None


class NFCeResponse(BaseModel):
    store: NFCeStore
    items: list[NFCeItem]
    total: float | None
```

---

## Benefícios dos DTOs

- validação automática
- tipagem forte
- integração Swagger
- serialização JSON automática
- documentação automática

---

# 7. nfce_routes.py

## Objetivo

Criar o endpoint HTTP.

## Código

```python
# src/routes/v1/nfce_routes.py

from http import HTTPStatus

from fastapi import APIRouter

from src.dtos.nfce_dtos import (
    NFCeParseRequest,
    NFCeResponse,
)
from src.services.nfce.nfce_service import parse_nfce

router = APIRouter(
    prefix='/nfce',
    tags=['nfce'],
)


@router.post(
    '/parse',
    status_code=HTTPStatus.OK,
    response_model=NFCeResponse,
)
async def parse_nfce_route(data: NFCeParseRequest):
    return await parse_nfce(data.url)
```

---

# Endpoint Final

## URL

```text
POST /v1/nfce/parse
```

---

## Body

```json
{
  "url": "https://www.fazenda.pr.gov.br/nfce/qrcode?..."
}
```

---

## Response

```json
{
  "store": {
    "name": "MILANO COMERCIO DE GENEROS ALIM.EIRELI"
  },
  "items": [
    {
      "name": "PAO FRANCES KG",
      "code": "3972",
      "quantity": 0.368,
      "unit": "KG",
      "unit_price": 13.98,
      "total_price": 5.14
    }
  ],
  "total": 5.14
}
```

---

# Como Executar o Projeto

## Instalar dependências

```bash
uv sync
```

---

## Instalar parser lxml

```bash
uv add lxml
```

---

## Rodar API

```bash
uvicorn src.main:app --reload
```

---

## Abrir Swagger

```text
http://127.0.0.1:8000/docs
```

---

# Possíveis Melhorias Futuras

## 1. Extrair mais campos

- CNPJ
- endereço
- data emissão
- forma pagamento
- chave acesso
- série
- número nota

---

## 2. Cache HTML

Evitar múltiplas requisições repetidas.

---

## 3. Suporte multiestado

Cada estado possui HTML diferente.

Estrutura futura:

```text
services/nfce/parsers/
├── pr_parser.py
├── sp_parser.py
├── mg_parser.py
```

---

## 4. Tratamento de erros

- timeout
- URL inválida
- nota inexistente
- bloqueios da SEFAZ

---

## 5. Testes automatizados

Criar:

- testes unitários
- mocks HTML
- validações parser

---

# Resultado Final

A integração permitiu:

- scraping NFC-e em produção
- integração completa FastAPI
- arquitetura modular
- documentação automática Swagger
- retorno estruturado JSON
- integração async
- separação clara de responsabilidades

---

# Como Executar o Projeto Localmente

Este guia descreve o processo completo para baixar, configurar e executar o projeto localmente.

---

# Pré-requisitos

Antes de iniciar, é necessário possuir instalado:

- Python 3.13+
- Git
- VS Code
- UV Package Manager

---

# 1. Clonar o Repositório

No terminal:

```bash
git clone URL_DO_REPOSITORIO
```

---

# 2. Entrar na Pasta do Projeto

```bash
cd notas-fiscais-python
```

---

# 3. Abrir no VS Code

```bash
code .
```

Ou abrir manualmente pelo VS Code.

---

# 4. Criar Arquivo .env

Duplicar:

```text
.env.example
```

para:

```text
.env
```

---

# 5. Instalar Dependências

No terminal:

```bash
uv sync
```

Esse comando irá:

- instalar dependências
- criar ambiente virtual
- sincronizar bibliotecas

---

# 6. Instalar lxml

Caso necessário:

```bash
uv add lxml
```

---

# 7. Ativar Ambiente Virtual

## Git Bash

```bash
source .venv/Scripts/activate
```

---

## PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
```

---

# 8. Executar a API

```bash
uvicorn src.main:app --reload
```

---

# 9. Abrir Swagger

Abrir no navegador:

```text
http://127.0.0.1:8000/docs
```

---

# 10. Testar Endpoint NFC-e

Endpoint:

```text
POST /v1/nfce/parse
```

---

## Body Exemplo

```json
{
  "url": "https://www.fazenda.pr.gov.br/nfce/qrcode?..."
}
```

---

## Resultado Esperado

```json
{
  "store": {
    "name": "MILANO COMERCIO DE GENEROS ALIM.EIRELI"
  },
  "items": [
    {
      "name": "PAO FRANCES KG",
      "code": "3972",
      "quantity": 0.368,
      "unit": "KG",
      "unit_price": 13.98,
      "total_price": 5.14
    }
  ],
  "total": 5.14
}
```

---

# Problemas Comuns

## Erro: lxml não encontrado

Instalar:

```bash
uv add lxml
```

---

## Erro: Variáveis de ambiente ausentes

Verificar existência do arquivo:

```text
.env
```

---

## Erro: Porta já em uso

Trocar porta:

```bash
uvicorn src.main:app --reload --port 8001
```

---

## Erro: Swagger não abre

Verificar se o terminal mostra:

```text
Application startup complete.
```

---

# Fluxo Completo de Execução

```text
Git Clone
   ↓
Abrir VS Code
   ↓
Criar .env
   ↓
uv sync
   ↓
Ativar .venv
   ↓
Rodar uvicorn
   ↓
Abrir Swagger
   ↓
Testar Endpoint NFC-e
```

---

# Conclusão

O módulo NFC-e foi implementado seguindo os padrões arquiteturais existentes do projeto.

A solução ficou:

- modular
- escalável
- organizada
- tipada
- assíncrona
- preparada para evolução futura

Além disso, a implementação validou que:

- a SEFAZ retorna HTML renderizado
- BeautifulSoup é suficiente
- não foi necessário Selenium ou Playwright
- HTTPX atende perfeitamente o fluxo
- FastAPI integrou sem necessidade de adaptações complexas
