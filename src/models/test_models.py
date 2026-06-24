from models.personal_details import PersonalDetails
from models.contact_info import ContactInfo

p_detail = PersonalDetails(
    first_name= "Alexander",
    last_name= "Alcazar"
)
for k,v in p_detail.to_dict().items():
    print(f"{k}: {v}")
