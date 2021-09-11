from fastapi import FastAPI, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from deta import Deta
from typing import Optional 
import send_mail
import id_handler
from datetime import date
import re
deta = Deta()

db_appointment_form = deta.Base("appointment-form")

db_sender_receiver_details = deta.Base("receiver-sender_details-appointment-form")

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AppointmentForm(BaseModel):
    first_name: str=Form(...)
    last_name: str=Form(...)
    appointment_date: str=Form(...)
    appointment_email: EmailStr=Form(...)
    subject: str=Form(...)
    message_body: str=Form(...)

class SenderReceiverDetails(BaseModel):
    sender_email: Optional[EmailStr]=None
    sender_password: Optional[str]=None
    receiver_email: Optional[EmailStr]=None

class SenderReceiverDetailswithID(BaseModel):
    id: int
    sender_email: Optional[EmailStr]=None
    sender_password: Optional[str]=None
    receiver_email: Optional[EmailStr]=None

@app.get("/")
async def read_root():
    return {"greetings": "Welcome to the Appointment Form API!"}

@app.get("/appointment-form",tags=["Appointment Form"])
async def get_appointment_form_details():
    '''
    Get all the messages from appointment form
    '''
    return next(db_appointment_form.fetch())

@app.get("/appointment-form/appointment-email/{appointment_email}",tags=["Appointment Form"])
async def get_appointment_form_details_by_appointment_email_id(appointment_email: EmailStr):
    '''
    Get messages from appointment form by email id.
    '''
    return next(db_appointment_form.fetch({"appointment_email":appointment_email}))

@app.get("/appointment-form/date/{appointment_date}",tags=["Appointment Form"])
async def get_appointment_form_details_by_appointment_email_id(appointment_date: str):
    '''
    Get messages from appointment form by date.
    Date format - DD-MM-YYYY
    '''
    return next(db_appointment_form.fetch({"appointment_date":appointment_date}))


@app.post("/appointment-form/",tags=["Appointment Form"])
async def post_appointment_form_details(appointment_form_object: AppointmentForm):
    '''
    A post request to send message.
    Date format - YYYY-MM-DD
    '''

    appointment_date = appointment_form_object.appointment_date
    if re.match("^(0[1-9]|[12][0-9]|3[01])[-](0[1-9]|1[012])[-](20)\d\d$",appointment_date):
        first_name = appointment_form_object.first_name
        last_name = appointment_form_object.last_name
        appointment_email = appointment_form_object.appointment_email
        subject= appointment_form_object.subject
        message_body = appointment_form_object.message_body
        send_mail_object = send_mail.SendEmail()
        send_mail_object.send_email(
            first_name = first_name,
            last_name = last_name,
            appointment_date=appointment_date,
            appointment_email=appointment_email,
            subject=subject,
            message_body=message_body)
        db_appointment_form.put(appointment_form_object.dict())
        return next(db_appointment_form.fetch())[-1]
    else:
        raise HTTPException(status_code=400, detail="Invalid Date")




@app.delete("/appointment-form-details/",tags=["Appointment Form"])
async def delete_sender_receiver_details(appointment_email: Optional[EmailStr]=None):
    '''
    Delete messages by email id.
    If you don't speicify email id. All the messages will be deleted.
    '''
    
    print(appointment_email)
    json_item = next(db_appointment_form.fetch())
    if not json_item:
        return {"task":"No Items to Delete"}

    if appointment_email == None:
        pass
    else:
        json_item = next(db_appointment_form.fetch({"appointment_email":appointment_email}))

    for dictionary in json_item:
        db_appointment_form.delete(dictionary["key"])

    return {"task":"Deleted Successfully"}



@app.get("/sender-receiver-details",tags=["Sender and Receiver Details"])
async def get_sender_receiver_details():
    '''
    Get all sender emails and receiver emails history.
    If 0 details exist. Then default environment variable's sender mail and receiver
    mail values are chosen.
    '''
    return next(db_sender_receiver_details.fetch())

@app.post("/sender-receiver-details/",tags=["Sender and Receiver Details"])
async def post_sender_receiver_details(sender_receiver_details: SenderReceiverDetails):
    '''
    Note: Give default sender_email as helplearnhome@gmail.com
    
    Post request for creating sender email and receiver email.
    Note that this is not related to the appointment email which is the email id of the patient.

    Sender email is just a server that sends the email to a receiving email id.

    By default you can keep sender_email as helplearnhome@gmail.com
    and give the receiving mail id where you want to receive the message as a doctor or receptionist.

    If you want to change server email then change the environment variable and create an app password and set it and run the server.
    '''
    sender_receiver_details_with_id = SenderReceiverDetailswithID(**sender_receiver_details.dict(),id=id_handler.auto_increment())
    db_sender_receiver_details.put(sender_receiver_details_with_id.dict())
    return {"task": "Added successfully", "item": sender_receiver_details_with_id.dict()}


@app.delete("/sender-receiver-details/delete-latest-added-item",tags=["Sender and Receiver Details"])
async def delete_sender_receiver_details_latest_added_item():
    '''
    Delete the last added sender and receiver mail details.
    '''
    json = next(db_sender_receiver_details.fetch())
    if not json:
        return {"task":"No Items to Delete"}

    latest_dictionary_item = id_handler.last_item()

    db_sender_receiver_details.delete(latest_dictionary_item["key"])

    return {"task":f"Deleted Successfully ", "Deleted item":latest_dictionary_item}


@app.delete("/sender-receiver-details/",tags=["Sender and Receiver Details"])
async def delete_sender_receiver_details_all_items():
    '''
    Delete all sender and receiver mail details from the database.
    '''
    json = next(db_sender_receiver_details.fetch())
    if not json:
        return {"task":"No Items to Delete"}
    
    json_item = next(db_sender_receiver_details.fetch())

    for dictionary in json_item:
        db_sender_receiver_details.delete(dictionary["key"])

    return {"task":"Deleted Successfully "}