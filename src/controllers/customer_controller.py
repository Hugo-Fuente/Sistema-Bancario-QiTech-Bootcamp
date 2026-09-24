from datetime import date
from controllers.base_controller import BaseController
from errors.custom_errors import (
    InvalidDocumentNumber, 
    DuplicatedDocumentNumber, 
    DuplicatedEmail, 
    UnderageCustomer,
    InvalidBirthdate # Importante importar isto!
)
from repositories import CustomerRepository
from dtos import CustomerDTO
from utils.document_number import is_valid_cpf

class CustomerController(BaseController):
    def __init__(self) -> None:
        super().__init__(__name__)
        self.customer_repository = CustomerRepository(self.context)

    def _parse_birthdate(self, raw_birthdate: str) -> date:
        """Converte a data, ou recusa com 422 em vez de 500, como na Sample Entity."""
        try:
            return date.fromisoformat(raw_birthdate)
        except ValueError:
            raise InvalidBirthdate(raw_birthdate)

    def _age_in_years(self, birthdate: date) -> int:
        today = date.today()
        age = today.year - birthdate.year

        if (today.month, today.day) < (birthdate.month, birthdate.day):
            age = age - 1

        return age

    def create(self, customer_data: dict) -> dict:
        self.logger.debug("A criar um novo Customer")
        
        document_number = customer_data["document_number"]
        email = customer_data["email"]
        birthdate = self._parse_birthdate(customer_data["birthdate"])

        # 1. Valida se o CPF é um número válido (matematicamente)
        if not is_valid_cpf(document_number):
            raise InvalidDocumentNumber(document_number)

        # 2. Valida duplicidade de CPF e Email
        if self.customer_repository.get_by_document_number(document_number) is not None:
            raise DuplicatedDocumentNumber(document_number)

        if self.customer_repository.get_by_email(email) is not None:
            raise DuplicatedEmail(email)

        # 3. Valida maioridade
        age = self._age_in_years(birthdate)
        if age < 18:
            raise UnderageCustomer(age, 18)

        # 4. Se passou em tudo, manda criar no repositório
        customer = self.customer_repository.create(customer_data)
        
        # 5. O Controller faz o commit para salvar de vez no banco!
        self.session.commit()

        # 6. Devolvemos apenas a chave usando o DTO
        return CustomerDTO.only_obj_key(customer)