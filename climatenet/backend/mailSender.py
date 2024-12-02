from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMessage, get_connection
from mailersend import emails
import os


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