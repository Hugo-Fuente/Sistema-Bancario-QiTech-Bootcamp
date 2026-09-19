# Estágio 1: Base
FROM python:3.11-slim as base

WORKDIR /app

# Copia apenas o arquivo de requisitos primeiro para otimizar o cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Estágio 2: API
FROM base as api

# Copia o restante do código do projeto
COPY . .

# Inicia o servidor FastAPI usando o Uvicorn, apontando para src/app.py
CMD ["uvicorn", "src.app:application", "--host", "0.0.0.0", "--port", "8000", "--reload"]