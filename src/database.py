import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Recupera a URL de conexão repassada pelo ambiente do Docker
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# Cria o motor de conexão com o banco de dados
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Cria a classe base de sessões ("Session Basics" da doc do SQLAlchemy)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)