class ContactInfo:
    """
    Represents secondary personal details attached to a system user.
    Handles physical address and communication fields.
    """
    def __init__(
        self,
        phone_number: str = None,
        street_address: str = None,
        city: str = None,
        state: str = None,
        zip_code: str = None
    ):
        self.phone_number = phone_number
        self.street_address = street_address
        self.city = city
        self.state = state
        self.zip_code = zip_code

    def to_dict(self) -> dict:
        """
        Flattens the contact details into a dictionary for network transmission.
        """
        return {
            "phone_number": self.phone_number,
            "street_address": self.street_address,
            "city": self.city,
            "state": self.state,
            "zip_code": self.zip_code
        }