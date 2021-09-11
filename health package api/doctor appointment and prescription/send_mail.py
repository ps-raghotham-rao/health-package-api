import smtplib
from email.message import EmailMessage
import os
import main
import id_handler

'''
To update .env in deta.sh  use these commands deta update -e <env_file_name> and 
uncomment below two lines while deploying because dotenv load module is not used by deta.sh
The update command is used to update env not load_dotenvv
These two below commands are required to update environmental variables in local machine.
If you want to run the fastapi in local server using uvicorn
'''
# from dotenv import load_dotenv
# load_dotenv()


class SendEmail:
    SMTP_GMAIL_SERVER = "smtp.gmail.com"
    SMTP_GMAIL_PORT = 465
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")
    receiver_email= os.getenv("RECEIVER_EMAIL")
    
    # @classmethod
    # def sender_receiver_details(cls,sender_email,receiver_email):
    #     if sender_email != None:
    #         cls.sender_email=sender_email
    #     if receiver_email != None:
    #         cls.receiver_email = receiver_email

    #this won't work if we redeploy the database with some changes As all the variables would be destroyed and redeclared.

    def send_email(self,first_name,last_name,appointment_date,appointment_email,subject,message_body): 

        db_sender_receiver_details_json = next(main.db_sender_receiver_details.fetch())


        self.first_name = first_name
        self.last_name = last_name
        self.appointment_date = appointment_date
        self.appointment_email = appointment_email
        self.subject="Appointment Form: "+subject
        self.message_body = f"Name: {first_name} {last_name}\n\nEmail: {appointment_email} \n\n Appointment Date {appointment_date} \n\n{message_body}"

        if db_sender_receiver_details_json:
            db_sender_receiver_details_last_object = id_handler.last_item()
            if db_sender_receiver_details_last_object['sender_email']!=None:
                self.sender_email=db_sender_receiver_details_last_object['sender_email']
            if db_sender_receiver_details_last_object['receiver_email']!=None:
                self.receiver_email=db_sender_receiver_details_last_object['receiver_email']
            if db_sender_receiver_details_last_object['sender_password']!=None:
                self.sender_password=db_sender_receiver_details_last_object['sender_password']
        
        # print(self.sender_email,self.sender_password,self.receiver_email)
        self.msg = EmailMessage()
        self.msg["From"] = self.sender_email
        self.msg["To"] = self.receiver_email
        self.msg['Subject'] = self.subject
        self.msg.set_content(self.message_body)

        server = smtplib.SMTP_SSL(self.SMTP_GMAIL_SERVER,self.SMTP_GMAIL_PORT)
        server.login(self.sender_email,self.sender_password)
        server.send_message(self.msg)
        server.quit