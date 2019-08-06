#!/usr/bin/env python3

import smtplib, os
from email.mime.text import MIMEText

sender = 'dapps-approvals@status.im'
receiver = 'dapps-approvals@status.im'

smtp_port = 587
smtp_host = "email-smtp.us-east-1.amazonaws.com"
smtp_user = os.environ["SMTP_USER"]
smtp_pass = os.environ["SMTP_PASS"]

msg = MIMEText('This is test mail')

msg['Subject'] = 'SES SMTP Test mail'
msg['From'] = sender
msg['To'] = receiver

with smtplib.SMTP(smtp_host, smtp_port) as server:
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(smtp_user, smtp_pass)
    rval = server.sendmail(sender, receiver, msg.as_string())

print('mail successfully sent')
