# Sistema Bancário - QiTech Bootcamp

Repositório dedicado ao desenvolvimento do Sistema Bancário como parte do QiTech Bootcamp.

## 🛠 Tecnologias Utilizadas

A stack tecnológica do projeto está rigorosamente definida para garantir consistência entre os ambientes de toda a equipe:
*   **Linguagem:** Python 3.11
*   **API:** FastAPI (v0.141.1) com validação via jsonschema
*   **Banco de Dados:** PostgreSQL 16 orquestrado via SQLAlchemy (v2.0.23) e psycopg2-binary
*   **Ambiente/Orquestração:** Docker e Docker Compose
*   **Testes:** pytest (v7.4.4)
*   **Integrações:** requests (v2.32.3) para chamadas a outros serviços (ex: API de boletos mockada)

## 👥 Equipe

*   **Hugo Gomes de La Fuente** - Configuração e Desenvolvimento
*   **Mateus Carósio** - Desenvolvimento
*   **Leandro Apolinário Leite** - Desenvolvimento

## ⚙️ Como Executar o Projeto (Localmente)

### 1. Pré-requisitos
Não é necessário instalar o Python diretamente na máquina para rodar a aplicação, pois o projeto inteiro sobe através do Docker. Certifique-se apenas de que você tem o **Docker** e o **Docker Compose** instalados.

### 2. Configuração Inicial
Clone este repositório e crie o seu arquivo de variáveis de ambiente local:

```bash
git clone [https://github.com/seu-usuario/Sistema-Bancario-QiTech-Bootcamp.git](https://github.com/seu-usuario/Sistema-Bancario-QiTech-Bootcamp.git)
cd Sistema-Bancario-QiTech-Bootcamp
cp .env.example .env
```

### 3. Levantar os Contêineres
Para iniciar o projeto inteiro (banco de dados e API), execute o comando principal:

```bash
docker compose up
```
*(Nota: O FastAPI utiliza `depends_on: condition: service_healthy` no `docker-compose.yml`, o que significa que a API aguarda o banco de dados estar pronto antes de iniciar).*

Caso o banco de dados fique em um estado inconsistente e você precise recomeçar do zero (apagar o banco e recriar o schema), utilize:

```bash
docker compose down -v
```

## 🧪 Como Rodar os Testes

Os testes são executados na máquina local, apontando para a API que o Docker acabou de levantar. 

1. Aguarde a API atingir o estado `healthy`.
2. Instale as dependências de desenvolvimento e execute o pytest:

```bash
pip install -r requirements-dev.txt
pytest
```

Para rodar um teste específico sem esperar pela suíte inteira:

```bash
pytest -v caminho::nome_do_teste
```

---
**Regra da Equipe:** Todo o código novo deve ser feito em uma branch separada (`feature/nome-da-tarefa`) e integrado na `main` apenas através de um Pull Request com revisão.
