from fastapi import FastAPI
from src.database import engine
from src.models import Base

application = FastAPI(
    title="Sistema Bancário API",
    description="API do Bootcamp QiTech"
)

# Este comando cria as tabelas na base de dados assim que a API arranca
Base.metadata.create_all(bind=engine)

@application.get("/")
def health_check():
    return {"status": "API rodando com sucesso!"}