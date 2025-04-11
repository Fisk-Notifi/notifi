import json
class Label:
    def __init__(self, recipient_name, recipient_address):
        self.recipient_name = recipient_name
        self.recipient_address = recipient_address

def json_to_label(json_data):
    json_data = json.loads(json_data)
    label = Label(
        json_data["document"]["inference"]["prediction"]["recipient_names"][0]["value"],
        json_data["document"]["inference"]["prediction"]["recipient_addresses"][0]["complete"]
    )
    return label