import os
import ssl
import smtplib
from email.message import EmailMessage
from email.headerregistry import Address

smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
smtp_port = os.getenv("SMTP_PORT", 465)
email_user = os.getenv("EMAIL_USER")
email_pw = os.getenv("EMAIL_PW")
domain = os.getenv("EMAIL_DOMAIN")
SENDER = "Counselling Service System"

# Create a secure SSL context
context = ssl.create_default_context()


class EmailService:
    default_subject = 'Assignment Alert'
    default_msg = 'You have an incoming chat request, please click the link to enter the chat room.'

    def __init__(self, server, port, user, pw):
        self.server = server
        self.port = port
        self.user = user
        self.pw = pw

    def compose(self, destination: Address, message: str) -> EmailMessage:
        msg = EmailMessage()
        msg['Subject'] = self.default_subject
        msg['From'] = Address(SENDER, self.user, domain)
        msg['To'] = destination

        msg.set_content(f"""
                Hi Counsellor,

                    {message}

                {SENDER}
                """)

        return msg

    def send(self, destination: Address, message: str = None):
        message = message if not message else self.default_msg

        msg = self.compose(destination, message)

        with smtplib.SMTP_SSL(self.server, self.port, context=context) as server:
            server.login(self.user, self.pw)
            server.send_message(msg)


email_service = EmailService(smtp_server, smtp_port, email_user, email_pw)
