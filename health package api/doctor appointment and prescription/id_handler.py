import main
from deta import Deta
def auto_increment():
    if next(main.db_sender_receiver_details.fetch()):
        json = next(main.db_sender_receiver_details.fetch())
        json = sorted(json,key=lambda object: object["id"])
        db_id = json[-1]["id"]
        db_id+=1
        return db_id
    db_id=1
    return db_id


def last_item():
    json = next(main.db_sender_receiver_details.fetch())
    json = sorted(json,key=lambda object: object["id"])
    last_json_object = json[-1]
    return last_json_object