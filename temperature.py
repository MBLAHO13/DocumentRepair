#!/usr/bin/python
# -*- coding: utf-8 -*-
# This script written to moniotr the Pi's temperature.
# Colleen Blaho - 2014 ENGR 103

import subprocess
import smtplib
import socket
from email.mime.text import MIMEText
import datetime
import os

#grab temperature
res = os.popen('vcgencmd measure_temp').readline()
temperatureString = (str(res).replace("temp=","").replace("'C\n",""))
temperatureString = float(temperatureString)

#begin logging
today = datetime.datetime.now()
f = open('templogging', 'a')
f.write(str(today))


if temperatureString > 60.0: 
	to = 'cpb49@drexel.edu'
	gmail_user = 'colleen.blaho@gmail.com'
	gmail_password = 'battery13lamp'
	smtpserver = smtplib.SMTP('smtp.gmail.com', 587)
	smtpserver.ehlo()
	smtpserver.starttls()
	smtpserver.ehlo
	smtpserver.login(gmail_user, gmail_password)
	msg = MIMEText(temperatureString)
	msg['Subject'] = 'TEMPERATURE ALERT!'
	msg['From'] = gmail_user
	msg['To'] = to
	smtpserver.sendmail(gmail_user, [to], msg.as_string())
	smtpserver.quit()
	f.write('BAD\n')
else:
	f.write('GOOD\n')
f.close()
