from fastapi import status
from fastapi.responses import JSONResponse
from utils.schema_handler import SchemaHandler
from fastapi import status, Header

class ClienteResource:

    # O decorator garante que só entra o que o JSON permitir
    @SchemaHandler.validate("post_cliente.json")
    def on_post(self, payload: dict, internal_token: str = Header(default="default_token", alias="INTERNAL-TOKEN")) -> JSONResponse:
        
        return JSONResponse(
            content={
                "mensagem": "Garçom (Resource) recebeu o pedido e o schema validou!", 
                "dados": payload
            },
            status_code=status.HTTP_201_CREATED,
        )