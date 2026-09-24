from fastapi import status, Header
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from controllers.customer_controller import CustomerController
from utils.schema_handler import SchemaHandler

class CustomerResource:
    @SchemaHandler.validate("post_customer.json")
    def on_post(self, payload: dict, internal_token: str = Header(default="default_token", alias="INTERNAL-TOKEN")) -> JSONResponse:
        controller = CustomerController()
        customer_dto = controller.create(payload)
        
        return JSONResponse(
            content=jsonable_encoder(customer_dto),
            status_code=status.HTTP_201_CREATED,
        )