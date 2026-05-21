# 🔧 Plano de Refatoração — Princípio DRY & Abstrações

> **Projeto:** Notas Fiscais API (FastAPI + SQLAlchemy Async)  
> **Data:** 2026-05-21  
> **Objetivo:** Eliminar duplicações de código, aplicar o princípio DRY em todas as camadas e propor abstrações para melhorar a manutenabilidade.

---

## 📋 Sumário

1. [Duplicações Encontradas](#1-duplicações-encontradas)
2. [Plano de Correção por Camada](#2-plano-de-correção-por-camada)
3. [Propostas de Abstrações](#3-propostas-de-abstrações)
4. [Ordem de Execução](#4-ordem-de-execução)

---

## 1. Duplicações Encontradas

### 🔴 Severidade Alta (Impacto direto na manutenabilidade)

#### DRY-01 — Padrão `find_by_<field>` repetido em todos os repositórios

```python
# Padrão idêntico repetido em 4 repositórios — só muda o campo de filtro:
async def find_by_<field>(self, value) -> Entity | None:
    result = await self.session.execute(
        self._base_query().where(Entity.field == value)
    )
    return result.scalar_one_or_none()
```

| Repositório | Método | Campo |
|-------------|--------|-------|
| `user_repository.py` | `find_by_email()` | `email` |
| `establishment_repository.py` | `find_by_tin()` | `business_tin` |
| `permission_repository.py` | `find_by_name()` | `name` |
| `invoice_repository.py` | `find_by_url()` | `source_url` |

**Problema:** 4 métodos com a **mesma** estrutura de 3 linhas, diferindo apenas no campo de filtro. Cada novo repositório precisará copiar e colar esse padrão.

---

#### DRY-02 — Padrão `find_paginated` duplicado nos repositórios

```python
# Bloco quase idêntico em 3 repositórios:
async def find_paginated_by_*(self, ..., page, per_page) -> tuple[Sequence[T], int]:
    query = self._base_query().where(...)

    count_query = select(func.count()).select_from(query.subquery())
    total = (await self.session.execute(count_query)).scalar_one()

    offset = (page - 1) * per_page
    items = (
        (await self.session.execute(query.offset(offset).limit(per_page)))
        .scalars().unique().all()
    )
    return items, total
```

| Repositório | Método |
|-------------|--------|
| `base_repository.py` | `find_paginated()` |
| `invoice_repository.py` | `find_paginated_by_user()` |
| `invoice_item_repository.py` | `find_paginated_by_invoice()` |

**Problema:** O cálculo de paginação (count + offset + limit) é copiado literalmente. Apenas o `where()` adicional muda.

---

#### DRY-03 — Padrão `find_by_X_and_user` repetido no `InvoiceRepository`

```python
# 4 métodos com lógica muito similar, diferindo apenas nas options de eager loading:
find_by_url(url)                      # _base_query + selectinload(items) + where(url)
find_by_id_with_user(id)              # _base_query + selectinload(user) + where(id)
find_by_id_and_user(id, user_id)      # _base_query + where(id) + where(user_id)
find_by_id_with_user_scoped(id, uid)  # _base_query + selectinload(user) + where(id) + where(user_id)
find_by_url_and_user(url, user_id)    # _base_query + selectinload(items) + where(url) + where(user_id)
```

**Problema:** 5 métodos onde a lógica base é a mesma, mas as combinações de `where` e `options(selectinload(...))` variam. Isso poderia ser resolvido com um query builder composável.

---

#### DRY-04 — Handlers de exceção repetitivos em `handlers.py`

```python
# 7 exception handlers com a MESMA estrutura — só muda o status code e o tipo da exceção:
@app.exception_handler(XxxException)
async def xxx_handler(request: Request, exc: XxxException) -> JSONResponse:
    return JSONResponse(
        status_code=HTTPStatus.XXX,
        content={'detail': exc.detail},
    )
```

| Handler | Exception | Status Code |
|---------|-----------|-------------|
| `not_found_handler` | `NotFoundException` | `404` |
| `conflict_handler` | `ConflictException` | `409` |
| `unauthorized_handler` | `UnauthorizedException` | `401` |
| `forbidden_handler` | `ForbiddenException` | `403` |
| `validation_handler` | `ValidationException` | `422` |
| `nfce_scraping_handler` | `NfceScrapingException` | `502` |
| `app_exception_handler` | `AppException` | `400` |

**Problema:** 7 funções idênticas com ~5 linhas cada. Ao criar uma nova exceção, é necessário adicionar mais um handler manualmente.

---

#### DRY-05 — Factory functions de repositório repetitivas em `dependencies.py`

```python
# 5 funções seguem exatamente o mesmo padrão:
async def get_<name>_repository(session: Session) -> XxxRepository:
    return XxxRepository(session)
```

| Função | Repositório |
|--------|-------------|
| `get_user_repository` | `UserRepository` |
| `get_refresh_token_repository` | `RefreshTokenRepository` |
| `get_establishment_repository` | `EstablishmentRepository` |
| `get_invoice_repository` | `InvoiceRepository` |
| `get_invoice_item_repository` | `InvoiceItemRepository` |

**Problema:** 5 funções boilerplate idênticas + 5 `Annotated` type aliases. Qualquer novo repositório requer mais boilerplate.

---

### 🟡 Severidade Média

#### DRY-06 — Construção de `PaginatedResponse.create()` repetida nas actions

```python
# Padrão repetido em 3 métodos de actions:
items, total = await self.repository.find_paginated(...)
return PaginatedResponse.create(
    items=list(items), total=total, page=page, per_page=per_page
)
```

| Action | Método |
|--------|--------|
| `BaseActions.list_paginated()` | Genérico |
| `InvoiceActions.list_paginated_by_user()` | Com filtro de usuário |
| `InvoiceActions.list_items_paginated()` | Com filtro de invoice |

---

#### DRY-07 — `_get_or_raise` pattern duplicado em `InvoiceActions`

```python
# BaseActions já tem _get_or_raise, mas InvoiceActions reimplementa variantes:

# Em base_actions.py:
async def _get_or_raise(self, id: int) -> T:
    entity = await self.repository.find_by_id(id)
    if not entity:
        raise NotFoundException(f'{self._entity_name} not found')
    return entity

# Em invoice_actions.py (reimplementação parcial):
async def find_with_user_scoped(self, id: int, user_id: int) -> InvoiceEntity:
    entity = await self.invoice_repo.find_by_id_with_user_scoped(id, user_id)
    if not entity:
        raise NotFoundException(f'{self._entity_name} not found')
    return entity
```

**Problema:** O padrão "busca + raise se None" é reimplementado sempre que se precisa de uma variante com filtro diferente.

---

#### DRY-08 — Import de `from_attributes=True` via `ConfigDict` repetido em DTOs

```python
# Repetido em 6 DTOs de resposta:
model_config = ConfigDict(from_attributes=True)
```

| DTO |
|-----|
| `EstablishmentResponse` |
| `InvoiceItemResponse` |
| `InvoiceUserResponse` |
| `InvoiceResponse` |
| `UserRead` |
| `PermissionRead` |

**Problema:** Menor, mas sugere a criação de um `BaseReadDTO` com essa configuração pré-definida.

---

#### DRY-09 — `ConfigDict(extra='forbid')` repetido em DTOs de escrita

```python
# Repetido em 4 DTOs:
model_config = ConfigDict(extra='forbid')
```

| DTO |
|-----|
| `UserCreate` |
| `UserUpdate` |
| `UserChangePassword` |
| `PermissionCreate` |

---

### 🟢 Severidade Baixa

#### DRY-10 — Construtores dos repositórios filhos são todos idênticos

```python
# Idêntico em TODOS os 6 repositórios:
def __init__(self, session: AsyncSession):
    super().__init__(EntityClass, session)
```

**Nota:** Aceitável em Python, mas pode ser automatizado com metaclass ou `__init_subclass__`.

---

#### DRY-11 — Import do `permission_entity.py` está quebrado

```python
# ERRADO (falta 'src.'):
from entities.base_entities import EntityMixin

# CORRETO:
from src.entities.base_entities import EntityMixin
```

**Problema:** Bug de importação. Não é duplicação, mas foi detectado durante a análise.

---

## 2. Plano de Correção por Camada

### 📦 Camada Exceptions (`src/exceptions/`)

#### [MODIFY] [base_exceptions.py](file:///C:/Users/mateus.serafim/Documents/unicv-dev/python/fastapi/notas-fiscais-python/src/exceptions/base_exceptions.py)

Adicionar `status_code` diretamente em cada classe de exceção para eliminar o mapeamento manual nos handlers:

```python
from http import HTTPStatus


class AppException(Exception):
    """Base exception for application errors."""
    status_code: HTTPStatus = HTTPStatus.BAD_REQUEST

    def __init__(self, detail: str):
        self.detail = detail


class NotFoundException(AppException):
    status_code = HTTPStatus.NOT_FOUND

class ConflictException(AppException):
    status_code = HTTPStatus.CONFLICT

class UnauthorizedException(AppException):
    status_code = HTTPStatus.UNAUTHORIZED

class ForbiddenException(AppException):
    status_code = HTTPStatus.FORBIDDEN

class ValidationException(AppException):
    status_code = HTTPStatus.UNPROCESSABLE_ENTITY

class NfceScrapingException(AppException):
    status_code = HTTPStatus.BAD_GATEWAY
```

#### [MODIFY] [handlers.py](file:///C:/Users/mateus.serafim/Documents/unicv-dev/python/fastapi/notas-fiscais-python/src/exceptions/handlers.py)

Substituir 7 handlers por **1 único** handler genérico:

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.exceptions.base_exceptions import AppException


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def app_exception_handler(
        request: Request, exc: AppException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={'detail': exc.detail},
        )
```

> **Redução:** De ~70 linhas para ~12 linhas. Novas exceções são tratadas automaticamente.

---

### 📦 Camada Repositories (`src/repositories/`)

#### [MODIFY] [base_repository.py](file:///C:/Users/mateus.serafim/Documents/unicv-dev/python/fastapi/notas-fiscais-python/src/repositories/base_repository.py)

Adicionar métodos genéricos para eliminar repetições nos repositórios filhos:

```python
# Adicionar ao BaseRepository:

async def find_one_by(self, **kwargs) -> T | None:
    """Busca genérica por campo(s). Ex: find_one_by(email='x@y.com')"""
    query = self._base_query()
    for field, value in kwargs.items():
        column = getattr(self.model, field)
        query = query.where(column == value)
    result = await self.session.execute(query)
    return result.unique().scalar_one_or_none()

async def find_all_by(self, **kwargs) -> Sequence[T]:
    """Busca genérica que retorna múltiplos registros."""
    query = self._base_query()
    for field, value in kwargs.items():
        column = getattr(self.model, field)
        query = query.where(column == value)
    result = await self.session.execute(query)
    return result.scalars().unique().all()

async def create_bulk(self, entities: list[T]) -> list[T]:
    """Criação em batch — movido do InvoiceItemRepository."""
    self.session.add_all(entities)
    await self.session.commit()
    for entity in entities:
        await self.session.refresh(entity)
    return entities

async def _paginate_query(self, query, page: int = 1, per_page: int = 20) -> tuple[Sequence[T], int]:
    """Lógica de paginação extraída para reuso."""
    count_query = select(func.count()).select_from(query.subquery())
    total = (await self.session.execute(count_query)).scalar_one()

    offset = (page - 1) * per_page
    items = (
        (await self.session.execute(query.offset(offset).limit(per_page)))
        .scalars().unique().all()
    )
    return items, total

async def find_paginated(self, page: int = 1, per_page: int = 20) -> tuple[Sequence[T], int]:
    """Refatorado para usar _paginate_query."""
    return await self._paginate_query(self._base_query(), page, per_page)
```

#### Impacto nos repositórios filhos:

**[MODIFY] [user_repository.py](file:///C:/Users/mateus.serafim/Documents/unicv-dev/python/fastapi/notas-fiscais-python/src/repositories/user_repository.py)**
```python
# ANTES — método custom:
async def find_by_email(self, email: str) -> UserEntity | None:
    result = await self.session.execute(
        self._base_query().where(UserEntity.email == email)
    )
    return result.scalar_one_or_none()

# DEPOIS — pode delegar ao base (escolher uma das opções):
# Opção A: Remover o método e chamar find_one_by(email=...) direto
# Opção B: Manter como alias para legibilidade
async def find_by_email(self, email: str) -> UserEntity | None:
    return await self.find_one_by(email=email)
```

**[MODIFY] [establishment_repository.py](file:///C:/Users/mateus.serafim/Documents/unicv-dev/python/fastapi/notas-fiscais-python/src/repositories/establishment_repository.py)** — mesma simplificação (`find_by_tin` → `find_one_by(business_tin=...)`)

**[MODIFY] [permission_repository.py](file:///C:/Users/mateus.serafim/Documents/unicv-dev/python/fastapi/notas-fiscais-python/src/repositories/permission_repository.py)** — mesma simplificação (`find_by_name` → `find_one_by(name=...)`)

**[MODIFY] [invoice_item_repository.py](file:///C:/Users/mateus.serafim/Documents/unicv-dev/python/fastapi/notas-fiscais-python/src/repositories/invoice_item_repository.py)** — `create_bulk` move para o base; `find_paginated_by_invoice` usa `_paginate_query`:
```python
async def find_paginated_by_invoice(
    self, invoice_id: int, page: int = 1, per_page: int = 20
) -> tuple[Sequence[InvoiceItemEntity], int]:
    query = self._base_query().where(InvoiceItemEntity.invoice_id == invoice_id)
    return await self._paginate_query(query, page, per_page)
```

**[MODIFY] [invoice_repository.py](file:///C:/Users/mateus.serafim/Documents/unicv-dev/python/fastapi/notas-fiscais-python/src/repositories/invoice_repository.py)** — `find_paginated_by_user` usa `_paginate_query`; métodos `find_by_*` podem ser consolidados com um query builder (ver Abstração 2).

---

### 📦 Camada DTOs (`src/dtos/`)

#### [NEW] `src/dtos/base_dtos.py` — DTOs base com configuração compartilhada

```python
from pydantic import BaseModel, ConfigDict


class BaseReadDTO(BaseModel):
    """DTO base para respostas com from_attributes=True."""
    model_config = ConfigDict(from_attributes=True)


class BaseWriteDTO(BaseModel):
    """DTO base para escrita com extra='forbid'."""
    model_config = ConfigDict(extra='forbid')
```

#### [MODIFY] DTOs de resposta — herdar de `BaseReadDTO`

```python
# ANTES (repetido em 6 classes):
class EstablishmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    ...

# DEPOIS:
class EstablishmentResponse(BaseReadDTO):
    ...
```

#### [MODIFY] DTOs de escrita — herdar de `BaseWriteDTO`

```python
# ANTES (repetido em 4 classes):
class UserCreate(UserBase):
    model_config = ConfigDict(extra='forbid')
    ...

# DEPOIS:
class UserCreate(UserBase, BaseWriteDTO):
    ...
```

---

### 📦 Camada Dependencies (`src/dependencies.py`)

#### [MODIFY] [dependencies.py](file:///C:/Users/mateus.serafim/Documents/unicv-dev/python/fastapi/notas-fiscais-python/src/dependencies.py)

Criar factory genérica para repositórios:

```python
from typing import TypeVar, Type

T = TypeVar("T")


def _repository_dependency(repo_class: Type[T]):
    """Factory genérica para injeção de repositórios."""
    async def _get_repository(session: Session) -> T:
        return repo_class(session)
    # Preservar o nome da função para o FastAPI DI
    _get_repository.__name__ = f"get_{repo_class.__name__.lower()}"
    return _get_repository


# ANTES — 5 funções boilerplate:
# async def get_user_repository(session: Session) -> UserRepository:
#     return UserRepository(session)
# UserRepo = Annotated[UserRepository, Depends(get_user_repository)]
# ...

# DEPOIS — 5 linhas:
UserRepo = Annotated[UserRepository, Depends(_repository_dependency(UserRepository))]
RefreshTokenRepo = Annotated[RefreshTokenRepository, Depends(_repository_dependency(RefreshTokenRepository))]
EstablishmentRepo = Annotated[EstablishmentRepository, Depends(_repository_dependency(EstablishmentRepository))]
InvoiceRepo = Annotated[InvoiceRepository, Depends(_repository_dependency(InvoiceRepository))]
InvoiceItemRepo = Annotated[InvoiceItemRepository, Depends(_repository_dependency(InvoiceItemRepository))]
```

> **Redução:** De ~25 linhas (5 funções + 5 type aliases) para ~7 linhas.

---

### 📦 Camada Entities (`src/entities/`)

#### [BUGFIX] [permission_entity.py](file:///C:/Users/mateus.serafim/Documents/unicv-dev/python/fastapi/notas-fiscais-python/src/entities/permission_entity.py)

```diff
-from entities.base_entities import EntityMixin
+from src.entities.base_entities import EntityMixin
```

---

## 3. Propostas de Abstrações

### 🏗️ Abstração 1 — Query Builder composável no `InvoiceRepository`

O `InvoiceRepository` tem 5 métodos que são variações do mesmo tema. Proposta de um builder interno:

```python
class InvoiceRepository(BaseRepository[InvoiceEntity]):
    # ... __init__ e _base_query existentes ...

    def _query(self):
        """Retorna um query builder composável."""
        return InvoiceQueryBuilder(self)

    async def find_by_url(self, url: str) -> InvoiceEntity | None:
        return await (
            self._query()
            .with_items()
            .where_url(url)
            .first()
        )

    async def find_by_url_and_user(self, url: str, user_id: int) -> InvoiceEntity | None:
        return await (
            self._query()
            .with_items()
            .where_url(url)
            .where_user(user_id)
            .first()
        )


class InvoiceQueryBuilder:
    """Builder para compor queries no InvoiceRepository."""

    def __init__(self, repo: InvoiceRepository):
        self._repo = repo
        self._query = repo._base_query()

    def with_items(self):
        self._query = self._query.options(selectinload(InvoiceEntity.items))
        return self

    def with_user(self):
        self._query = self._query.options(selectinload(InvoiceEntity.user))
        return self

    def where_url(self, url: str):
        self._query = self._query.where(InvoiceEntity.source_url == url)
        return self

    def where_user(self, user_id: int):
        self._query = self._query.where(InvoiceEntity.user_id == user_id)
        return self

    async def first(self) -> InvoiceEntity | None:
        result = await self._repo.session.execute(self._query)
        return result.unique().scalar_one_or_none()

    async def paginated(self, page: int, per_page: int):
        return await self._repo._paginate_query(self._query, page, per_page)
```

> **Benefício:** Elimina a explosão combinatória de métodos `find_by_X_and_Y_with_Z`. Novos filtros são compostos em vez de escritos do zero.

---

### 🏗️ Abstração 2 — `_get_or_raise` genérico com callback

Estender o padrão existente para suportar qualquer consulta (não só `find_by_id`):

```python
class BaseActions(Generic[T]):
    # ... existente ...

    async def _get_or_raise(
        self,
        id: int | None = None,
        *,
        finder: Callable | None = None,
        message: str | None = None,
    ) -> T:
        """Busca genérica com raise automático.

        Uso:
            await self._get_or_raise(42)  # usa find_by_id
            await self._get_or_raise(finder=lambda: repo.find_by_url(url))
        """
        if finder:
            entity = await finder()
        elif id is not None:
            entity = await self.repository.find_by_id(id)
        else:
            raise ValueError("Either id or finder must be provided")

        if not entity:
            raise NotFoundException(message or f'{self._entity_name} not found')
        return entity
```

---

### 🏗️ Abstração 3 — DTO Mapper / Entity Builder

Centralizar conversões DTO → Entity para eliminar construção manual:

```python
# src/mappers/__init__.py

class EntityMapper:
    """Utilitário para converter DTOs Pydantic em entidades SQLAlchemy."""

    @staticmethod
    def to_entity(dto, entity_class, **extra_fields):
        """Converte um DTO em uma entidade."""
        data = dto.model_dump()
        data.update(extra_fields)
        return entity_class(**data)

    @staticmethod
    def to_entities(dtos, entity_class, **extra_fields):
        """Converte uma lista de DTOs em entidades."""
        return [
            EntityMapper.to_entity(dto, entity_class, **extra_fields)
            for dto in dtos
        ]
```

**Uso em `InvoiceActions.extract_and_persist`:**
```python
# ANTES (7 linhas):
items_to_create = [
    InvoiceItemEntity(
        invoice_id=invoice.id,
        description=item.description.upper(),
        code=item.code, unit=item.unit,
        quantity=item.quantity,
        unit_price=item.unit_price,
        total_price=item.total_price,
    )
    for item in parsed.items
]

# DEPOIS (1 linha + transformação):
items_to_create = EntityMapper.to_entities(
    parsed.items, InvoiceItemEntity,
    invoice_id=invoice.id,
    description_transform=lambda d: d.upper(),  # ou pré-processar
)
```

---

### 🏗️ Abstração 4 — Middleware para paginação automática

Extrair o padrão repetido de "chamar repo.find_paginated → empacotar em PaginatedResponse":

```python
# Adicionar ao BaseActions:
async def _paginated_query(
    self,
    finder: Callable[..., Awaitable[tuple[Sequence, int]]],
    page: int,
    per_page: int,
    **finder_kwargs,
) -> PaginatedResponse[T]:
    """Wrapper genérico para consultas paginadas."""
    items, total = await finder(page=page, per_page=per_page, **finder_kwargs)
    return PaginatedResponse.create(
        items=list(items), total=total, page=page, per_page=per_page
    )
```

**Uso:**
```python
# ANTES (InvoiceActions):
async def list_paginated_by_user(self, user_id, page, per_page):
    items, total = await self.invoice_repo.find_paginated_by_user(user_id, page, per_page)
    return PaginatedResponse.create(items=list(items), total=total, page=page, per_page=per_page)

# DEPOIS:
async def list_paginated_by_user(self, user_id, page, per_page):
    return await self._paginated_query(
        self.invoice_repo.find_paginated_by_user, page, per_page, user_id=user_id
    )
```

---

### 🏗️ Abstração 5 — `__init_subclass__` para auto-registro de repositórios

Eliminar o construtor boilerplate dos repositórios:

```python
class BaseRepository(Generic[T]):
    _model: type[T]

    def __init_subclass__(cls, model: type | None = None, **kwargs):
        super().__init_subclass__(**kwargs)
        if model is not None:
            cls._model = model

    def __init__(self, session: AsyncSession):
        self.model = self._model
        self.session = session

# Uso:
class UserRepository(BaseRepository[UserEntity], model=UserEntity):
    # Não precisa de __init__!
    pass
```

> **Benefício:** Elimina os 6 construtores idênticos (`super().__init__(EntityClass, session)`).

---

## 4. Ordem de Execução

A refatoração deve ser feita em fases para minimizar riscos:

### Fase 1 — Fundação (mudanças não-breaking)
| # | Tarefa | Arquivos | Risco |
|---|--------|----------|-------|
| 1.1 | Corrigir import quebrado em `permission_entity.py` | `permission_entity.py` | 🟢 Baixo |
| 1.2 | Adicionar `status_code` às exceções e simplificar handlers | `base_exceptions.py`, `handlers.py` | 🟢 Baixo |
| 1.3 | Adicionar `find_one_by`, `find_all_by`, `create_bulk`, `_paginate_query` ao `BaseRepository` | `base_repository.py` | 🟢 Baixo |

### Fase 2 — DTOs base e configuração
| # | Tarefa | Arquivos | Risco |
|---|--------|----------|-------|
| 2.1 | Criar `BaseReadDTO` e `BaseWriteDTO` | `dtos/base_dtos.py` [NEW] | 🟢 Baixo |
| 2.2 | Migrar DTOs de resposta para herdar de `BaseReadDTO` | `invoice_dtos.py`, `user_dtos.py`, `permission_dtos.py` | 🟡 Médio |
| 2.3 | Migrar DTOs de escrita para herdar de `BaseWriteDTO` | `user_dtos.py`, `permission_dtos.py` | 🟡 Médio |

### Fase 3 — Simplificação de Repositórios
| # | Tarefa | Arquivos | Risco |
|---|--------|----------|-------|
| 3.1 | Delegar `find_by_*` dos repos filhos para `find_one_by` | `user_repository.py`, `establishment_repository.py`, `permission_repository.py` | 🟡 Médio |
| 3.2 | Refatorar `find_paginated_by_*` para usar `_paginate_query` | `invoice_repository.py`, `invoice_item_repository.py` | 🟡 Médio |
| 3.3 | (Opcional) Implementar `InvoiceQueryBuilder` | `invoice_repository.py` | 🟡 Médio |
| 3.4 | (Opcional) Implementar `__init_subclass__` no base | `base_repository.py` e todos os repos | 🟡 Médio |

### Fase 4 — Dependencies e Actions
| # | Tarefa | Arquivos | Risco |
|---|--------|----------|-------|
| 4.1 | Criar `_repository_dependency` factory genérica | `dependencies.py` | 🟢 Baixo |
| 4.2 | Estender `_get_or_raise` com callback | `base_actions.py` | 🟢 Baixo |
| 4.3 | Adicionar `_paginated_query` helper ao `BaseActions` | `base_actions.py` | 🟢 Baixo |
| 4.4 | (Opcional) Criar módulo `src/mappers/` com `EntityMapper` | `mappers/__init__.py` [NEW] | 🟢 Baixo |

### Fase 5 — Verificação
| # | Tarefa |
|---|--------|
| 5.1 | Executar testes existentes para garantir que nada quebrou |
| 5.2 | Verificar que a aplicação inicia corretamente (`uvicorn`) |
| 5.3 | Testar endpoints via Swagger/OpenAPI |

---

## 📊 Resumo de Impacto

| Métrica | Antes | Depois (estimado) |
|---------|-------|--------------------|
| Linhas em `handlers.py` | ~70 | ~12 |
| `find_by_*` duplicados nos repos | 4 | 0 (delegam ao base) |
| Lógica de paginação duplicada | 3 cópias | 1 (no base) |
| Factory functions boilerplate | 5 | 1 (genérica) |
| `ConfigDict` repetido | 10 | 0 (herdado de DTOs base) |
| Construtores de repos idênticos | 6 | 0 (com `__init_subclass__`) |
| Arquivos novos necessários | — | 2 (`dtos/base_dtos.py`, `mappers/__init__.py`) |
| Métodos no `InvoiceRepository` | 7 | ~3 (com query builder) |
