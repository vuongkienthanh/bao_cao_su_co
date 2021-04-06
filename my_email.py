import sql
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os


def is_OK():
    return os.environ['EMAIL_NOTIFICATION'] == 'ON'


def mail(func):
    def inner(data):
        s = smtplib.SMTP(host=os.environ['email_server_host'], port=os.environ['email_server_port'])
        s.starttls()
        s.login(os.environ['sender_user'], os.environ['sender_password'])
        s.ehlo_or_helo_if_needed()
        func(s, data)
        s.quit()
    return inner


@mail
def sendmail(s, data):
    ls = sql.get_emails()
    msg = MIMEMultipart()
    msg['From'] = os.environ['sender_email']
    msg['To'] = ';'.join(ls)
    msg['Subject'] = "Bạn nhận được báo cáo mới"
    message = f"Bạn nhận được báo cáo mới với ID là {data['id']}.\n" +\
        f"Bạn có thể xem tại đây: {data['request'].url_for('homepage')}" +\
        f"get_report/{data['id']}"
    msg.attach(MIMEText(message, 'plain'))
    for receiver in ls:
        s.sendmail(os.environ['sender_email'], receiver, msg.as_string())


def get_receiver_emails():
    return [x for s in sql.get_emails() for x in s]


def add_receiver_email(email_):
    if sql.add_email(email_):
        return True


def remove_receiver_email(email_):
    if sql.remove_email(email_):
        return True
