import os
import ssl
import logging
import smtplib
import socket
from string import Formatter
from email.message import EmailMessage
from email.headerregistry import Address
from typing import Dict, List

logger = logging.getLogger(__name__)

smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
smtp_port = os.getenv("SMTP_PORT", 465)
email_user = os.getenv("EMAIL_USER", "sao")
email_pw = os.getenv("EMAIL_PW")
domain = os.getenv("EMAIL_DOMAIN", "gmail.com")
SENDER = "Student Affairs Office"
chatroom_url = 'http://localhost:8787/main/createRoom/'

# Create a secure SSL context
context = ssl.create_default_context()


class EmailTemplate:
    def __init__(self, subject: str, body: str):
        self._subject = subject
        self._body = body
        self.args = self.get_args(body)

    @property
    def subject(self):
        return self._subject

    @property
    def body(self):
        return self._body

    @staticmethod
    def get_args(input_string: str) -> List[str]:
        """
        Get all string formatting arguments from text, e.g. body

        :param input_string:
        :return:
        """
        return [fname for _, fname, _, _ in Formatter().parse(input_string) if fname]

    def render(self, template_data=None) -> str:
        """
        Render email template

        :param template_data:
        :return: rendered email message
        """
        if self.args:
            if set(self.args) != set(template_data.keys()):
                logger.debug("Keys in config map does not equals arguments in template!")
            message = self.body.format(**template_data)
        else:
            message = self.body

        return message


class EmailService:
    email_templates = {
        'new_assignment': EmailTemplate(subject="Requesting CWS Online Chat Service",
                                        body=f"""Dear Counsellor
            
We have received a request from a student for using our Online Chat Service just now.
Please click the following link to start the chat with the student accordingly.

{chatroom_url}

All the best, 
Counselling and Wellness Section
Student Affairs Office"""
                                        ),
        'appointment_request': EmailTemplate(subject="Making appointment with SAO counsellor",
                                             body="""Dear Counsellor

I would like to make appointment with SAO counsellor on the following date and time:
Date: {appointment_date}
Time: {appointment_time}

Looking forward to your reply.

Regards
{requester_name}"""
                                             )
    }

    def __init__(self, server, port, user, pw):
        self.server = server
        self.port = port
        self.user = user
        self.pw = pw

    def compose(self, destination: str, subject: str, msesage: str) -> EmailMessage:
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = Address(SENDER, self.user, domain)
        msg['To'] = destination

        msg.set_content(msesage)

        return msg

    def send(self, template_name: str, destination: str, template_data: Dict = None):
        template = self.email_templates[template_name]
        message = template.render(template_data)
        msg = self.compose(destination, template.subject, message)

        try:
            with smtplib.SMTP_SSL(self.server, self.port, context=context) as server:
                server.login(self.user, self.pw)
                server.send_message(msg)
        except socket.error as e:
            logger.warning(e)
        except Exception as e:
            logger.warning(e)


email_service = EmailService(smtp_server, smtp_port, email_user, email_pw)
