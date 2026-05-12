from sqlalchemy import (
    Column, String, Integer, BigInteger, ForeignKey,
    DateTime, Table
)
from sqlalchemy.orm import declarative_base, relationship
import uuid
from datetime import datetime

Base = declarative_base()


def generate_uuid():
    return str(uuid.uuid4())


# -------------------- ASSOCIATION TABLES --------------------

# relação N:N entre users e roles
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", String, ForeignKey("users.id")),
    Column("role_id", String, ForeignKey("roles.id"))
)

# relação N:N entre roles e permissions
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", String, ForeignKey("roles.id")),
    Column("permission_id", String, ForeignKey("permissions.id"))
)


# -------------------- USERS --------------------
class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime)
    deleted_at = Column(DateTime)

    roles = relationship("Role", secondary=user_roles, back_populates="users")
    refresh_tokens = relationship("RefreshToken", back_populates="user")

    # ✅ ADICIONADO
    invoices = relationship("Invoice", back_populates="user")


# -------------------- ROLES --------------------
class Role(Base):
    __tablename__ = "roles"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime)
    deleted_at = Column(DateTime)

    users = relationship("User", secondary=user_roles, back_populates="roles")
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")


# -------------------- PERMISSIONS --------------------
class Permission(Base):
    __tablename__ = "permissions"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String)

    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")


# -------------------- REFRESH TOKENS --------------------
class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.id"))
    token = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)

    user = relationship("User", back_populates="refresh_tokens")


# -------------------- STATES --------------------
class State(Base):
    __tablename__ = "states"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    code = Column(String, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    cities = relationship("City", back_populates="state")


# -------------------- CITIES --------------------
class City(Base):
    __tablename__ = "cities"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    state_id = Column(Integer, ForeignKey("states.id"))

    created_at = Column(DateTime, default=datetime.utcnow)

    state = relationship("State", back_populates="cities")
    establishments = relationship("Establishment", back_populates="city")


# -------------------- ESTABLISHMENTS --------------------
class Establishment(Base):
    __tablename__ = "establishments"

    id = Column(String, primary_key=True, default=generate_uuid)
    business_id = Column(String)
    name = Column(String)
    business_name = Column(String)

    city_id = Column(Integer, ForeignKey("cities.id"))

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime)
    deleted_at = Column(DateTime)

    city = relationship("City", back_populates="establishments")
    invoices = relationship("Invoice", back_populates="establishment")


# -------------------- INVOICES --------------------
class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"))
    establishment_id = Column(String, ForeignKey("establishments.id"))

    issue_date = Column(DateTime)
    total_value = Column(BigInteger)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime)
    deleted_at = Column(DateTime)

    establishment = relationship("Establishment", back_populates="invoices")
    items = relationship("InvoiceItem", back_populates="invoice")

    # ✅ ADICIONADO
    user = relationship("User", back_populates="invoices")


# -------------------- INVOICE ITEMS --------------------
class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id = Column(String, primary_key=True, default=generate_uuid)
    invoice_id = Column(String, ForeignKey("invoices.id"))

    quantity = Column(Integer)
    unit_price = Column(BigInteger)
    total_price = Column(BigInteger)

    description = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime)
    deleted_at = Column(DateTime)

    invoice = relationship("Invoice", back_populates="items")   