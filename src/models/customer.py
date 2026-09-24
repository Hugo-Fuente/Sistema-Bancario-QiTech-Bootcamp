from sqlalchemy import Column, Integer, String, Date, DateTime, CHAR
from sqlalchemy.sql import func
# Importamos a Base que já existe no projeto para manter a organização
from .base import Base 

class Customer(Base):
    __tablename__ = "customer"

    id = Column(Integer, primary_key=True, index=True)
    customer_key = Column(CHAR(36), nullable=False, unique=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    document_number = Column(CHAR(14), nullable=False, unique=True)
    birthdate = Column(Date, nullable=False)
    status = Column(String(50), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())