import logging
import os
import smtplib
import socket
import ssl
from email.headerregistry import Address
from email.message import EmailMessage
from string import Formatter
from typing import Dict, List

logger = logging.getLogger('django')

smtp_server = os.getenv("SMTP_SERVER", "smtp.office365.com")
smtp_port = os.getenv("SMTP_PORT", 587)
sender_user = os.getenv("SENDER_USER")
sender_pw = os.getenv("SENDER_PW")
sender_domain = os.getenv("SENDER_DOMAIN")

receiver_user = os.getenv("RECEIVER_USER")
receiver_domain = os.getenv("RECEIVER_DOMAIN")
sender_name = "Student Affairs Office"
chatroom_url = 'https://ics-sao.polyu.edu.hk/main/chat/counsellor_from_email/'
default_template_data = {
    'new_assignment': {
        'chatroom_url': chatroom_url
    },
    'appointment_request': {},
    'notification_student':{}
}

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
                                        body="""Dear Counsellor

We have received a request from a student for using our Online Chat Service just now.
Please click the following link to start the chat with the student accordingly.

{chatroom_url}?student_netid={student_netid}

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
                                             ),
        'notification_student': EmailTemplate(subject="Thank you for your interest in using CWS Online Chat Service",
                                             body="""Dear Student

Since you have not entered into the chat room, we are not able to provide the Online Chat Service. In case of need, you can contact our student counsellors through the below ways:

1. By phone at 2766 6800 during our office hours (Monday – Friday: 09.00 – 19.00). 
2. Email: stud.counselling@polyu.edu.hk 
3. PolyU LINE: Non-Office Hours Student Counselling Hotline Service 
·        Hotline: (852) 8100 1583
·        00.00 to 09.00 and 19.00 to 00.00 (Monday – Friday) 
·        00.00 to 09.00 and 12.00 to 00.00 (Saturday) 
·        24-hour round the clock on Sunday and Public Holidays 
 
In case of emergency or facing an imminent risk, please call the police at 999 for immediate assistance.

Thank you very much for your time.

All the best 
Counselling and Wellness Section
Student Affairs Office"""
                                             )
    }

    def __init__(self, server, port, user, pw):
        self.server = server
        self.port = port
        self.user = user
        self.pw = pw

    def compose(self, destination: str, subject: str, message: str) -> EmailMessage:
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = Address(sender_name, self.user, sender_domain)
        if DEBUG:
            msg['To'] = (Address(receiver_user, receiver_user, receiver_domain),
                     Address('16904228r', '16904228r', 'connect.polyu.hk'))
        else:
            msg['To'] = (Address(destination, destination, receiver_domain),
                     Address('16904228r', '16904228r', 'connect.polyu.hk'))

        msg.set_content(message)

        return msg

    def send(self, template_name: str, destination: str, template_data: Dict = None):
        logger.info("Composing email.")
        template = self.email_templates[template_name]
        if template_data is None:
            template_data = dict()
        combined_template_data = {**default_template_data.get(template_name, {}), **template_data}
        message = template.render(combined_template_data)
        msg = self.compose(destination, template.subject, message)

        try:
            with smtplib.SMTP(self.server, self.port) as server:
                # server.ehlo()
                # server.starttls()
                # server.login(f"{self.user}@{sender_domain}", self.pw)
                server.send_message(msg)
        except (socket.error, Exception) as e:
            logger.warning(e)
            logger.warning("Email sent fail.")

        logger.info("Successfully sent.")


email_service = EmailService(smtp_server, smtp_port, sender_user, sender_pw)

if __name__ == '__main__':
    template_data = {'student_netid': '12345678A'}
    #email_service.send('new_assignment', 'staff_id', template_data)
    email_service.send('notification_student', 'student_netid', template_data)
