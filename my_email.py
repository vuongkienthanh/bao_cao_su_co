from init import config_path
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# config
cf = json.load(open(config_path, mode="r", encoding='utf-8'))


# set up the SMTP server
def mail(func):
    def inner(typ, data):
        s = smtplib.SMTP(host=cf['server_host'], port=cf['server_port'])
        s.starttls()
        s.login(cf['login_user'], cf['login_password'])
        s.ehlo_or_helo_if_needed()
        func(s, typ, data)
        s.quit()
    return inner


@mail
def sendmail(s, typ, data):
    msg = MIMEMultipart()
    msg['From'] = cf['sender_email']
    msg['To'] = ';'.join(cf['receiver_email'])
    msg['Subject'] = "Bạn nhận được báo cáo mới"
    message = f"Bạn nhận được báo cáo {typ} mới với ID là {data['id']}.\n" +\
        f"Bạn có thể xem tại đây: {data['request'].url_for('homepage')}" +\
        f"{'get_quick_report' if typ=='nhanh' else 'get_report'}" +\
        f"/{data['id']}"
    msg.attach(MIMEText(message, 'plain'))
    for receiver in cf['receiver_email']:
        s.sendmail(cf['sender_email'], receiver, msg.as_string())


def get_receiver_emails():
    return cf['receiver_email']


def add_receiver_email(email_):
    global cf
    if not (email_ in cf['receiver_email']):
        cf['receiver_email'].append(email_)
        json.dump(cf, config_path)
        return True


def remove_receiver_email(email_):
    global cf
    if (email_ in cf['receiver_email']):
        cf['receiver_email'].remove(email_)
        json.dump(cf, config_path)
        return True
