import json
from fastapi import FastAPI, Body, HTTPException, Depends
from jsonschema import validate, ValidationError
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

# Importamos a sessão e o modelo criados nos passos anteriores
from src.database import engine, SessionLocal
from src.models import Base, Cliente

application = FastAPI(
    title="Sistema Bancário API",
    description="API do Bootcamp QiTech"
)

Base.metadata.create_all(bind=engine)

with open("src/schemas/cliente_create.json", "r") as f:
    cliente_schema = json.load(f)

# Função para garantir que a sessão da base de dados abre e fecha corretamente
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@application.get("/")
def health_check():
    return {"status": "API rodando com sucesso!"}

@application.get("/clientes")
def listar_clientes(db: Session = Depends(get_db)):
    # Consulta todos os clientes na base de dados
    clientes = db.query(Cliente).all()
    
    return {"total": len(clientes), "clientes": clientes}

# Adicionamos a injeção da sessão (db) nos parâmetros da rota
@application.post("/clientes", status_code=201)
async def criar_cliente(payload: dict = Body(...), db: Session = Depends(get_db)):
    
    # 1. Validação jsonschema
    try:
        validate(instance=payload, schema=cliente_schema)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.message)
    
    # 2. Gravação no PostgreSQL via SQLAlchemy
    novo_cliente = Cliente(
        nome=payload["nome"], 
        documento=payload["documento"]
    )
    db.add(novo_cliente)
    
    try:
        db.commit() 
        db.refresh(novo_cliente) 
    except IntegrityError:
        db.rollback() # Limpa a transação bloqueada no PostgreSQL
        raise HTTPException(status_code=409, detail="Já existe um cliente registado com este documento.")
    
    # 3. Retorno com os dados reais gravados
    return {
        "mensagem": "Cliente criado com sucesso!", 
        "id_cliente": novo_cliente.id,
        "dados": payload
    }