from models import Customer

class CustomerDTO:
    """Traduz o objeto do banco no JSON que a API devolve."""
    
    @staticmethod
    def only_obj_key(customer: Customer) -> dict:
        dto = dict()
        # Garante que devolvemos a key como string
        dto["customer_key"] = str(customer.customer_key)
        return dto

    @staticmethod
    def obj_to_dict(customer: Customer) -> dict:
        dto = dict()
        dto["customer_key"] = str(customer.customer_key)
        dto["name"] = customer.name
        dto["email"] = customer.email
        dto["document_number"] = customer.document_number
        dto["birthdate"] = customer.birthdate.isoformat()
        dto["status"] = customer.status
        
        # Só tenta usar isoformat se created_at existir
        if customer.created_at is not None:
            dto["created_at"] = customer.created_at.isoformat()
        else:
            dto["created_at"] = None
            
        return dto