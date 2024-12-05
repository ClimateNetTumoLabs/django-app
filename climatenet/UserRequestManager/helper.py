from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMessage, get_connection
from mailersend import emails
import requests
import os


def approve_user(form):
    request  =requests.api
    create_iot_thing = request.get('certificate endpoint')
    

def send_approval_email(user):
    mailer = emails.NewEmail()
    mailer = emails.NewEmail()
    print("done!!!!!!!!!!!!!!!!!")
    # define an empty dict to populate with mail values
    mail_body = {}

    mail_from = {
        "name": "Your Name",
        "email": "trial-x2p0347rp6kgzdrn.mlsender.net",
    }

    recipients = [
        {
            "name": "Recipient",
            "email": "rnobaboomian@gmail.com",
        }
    ]

    personalization = [
        {
            "email": "recipient@email.com",
            "data": {
                "name": ""
            }
        }
    ]

    mailer.set_mail_from(mail_from, mail_body)
    mailer.set_mail_to(recipients, mail_body)
    mailer.set_subject("Hello from {$company}", mail_body)
    mailer.set_template("z3m5jgrk96oldpyo", mail_body)
    # mailer.set_advanced_personalization(personalization, mail_body)

    mailer.send(mail_body)


import json
import os
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

def send_mail(recipient,subject,attachment,html_file_path,name=""):
    SENDER = "baboomian53@gmail.com"
    print("===========")
    print(recipient)
    print("===========")


    CHARSET = "utf-8"

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    html_file_path = os.path.join(BASE_DIR, "backend/html", html_file_path)
    try:
        with open(html_file_path, "r", encoding="utf-8") as html_file:
            BODY_HTML = html_file.read()
            BODY_HTML = BODY_HTML.replace("{{recipient_email}}", name)
            
    except FileNotFoundError:
        print(f"Error: HTML file not found at {html_file_path}")
        return
    except Exception as e:
        print(f"Error reading HTML file: {e}")
        return

    
    msg = MIMEMultipart('mixed')
    msg['Subject'] = subject
    msg['From'] = SENDER
    msg['To'] = recipient

    
    msg_body = MIMEMultipart('alternative')
    # textpart = MIMEText(body_text.encode(CHARSET), 'plain', CHARSET)
    htmlpart = MIMEText(BODY_HTML.encode(CHARSET), 'html', CHARSET)
    # msg_body.attach(textpart)
    msg_body.attach(htmlpart)
    msg.attach(msg_body)


    print(html_file_path)
    if (attachment is not None):
        attachment = os.path.join(BASE_DIR, "backend/html", attachment)
        print(attachment)
        with open(attachment, 'rb') as attachment_file:
            att = MIMEApplication(attachment_file.read())
            att.add_header('Content-Disposition', 'attachment', filename=os.path.basename(attachment))
        msg.attach(att)

    
    email_as_string = msg.as_string()

    
    payload = {
        "mail_data": email_as_string,
        "recipient": recipient
    }

    
    url = "https://4vvxx9iw2d.execute-api.us-east-1.amazonaws.com/testing/mailService"

    
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        
        if response.status_code == 200:
            print("Lambda function executed successfully!")
            print("Response:", response.json())
        else:
            print(f"Error triggering Lambda: {response.status_code}")
            print("Response:", response.text)
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

