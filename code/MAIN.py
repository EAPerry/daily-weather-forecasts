# -----------------------------------------------------------------------------
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Project Title: Daily Weather Forecast Data
# Script Title: MAIN
# -----------------------------------------------------------------------------
"""
The purpose of this script to perform the daily data pulls used to maintain the
data archive.
"""
# -----------------------------------------------------------------------------
# Contributor(s): Evan Perry
# Last Revised: 2023-09-09
# version = 1.0
# -----------------------------------------------------------------------------

###############################################################################
# Setup

import subprocess
import os
from datetime import date
import smtplib
import pandas as pd
from email.mime.text import MIMEText

repo_path = 'C:/Users/eaper/OneDrive/personal-website/daily-weather-forecasts'
os.chdir(repo_path)

api_key_file = "C:/Users/eaper/OneDrive/api-keys/gmail.txt"
with open(api_key_file) as f:
    API_KEY = f.readlines()[0]

###############################################################################


###############################################################################
# Grab todays data

# Daily Pulls - Counties
subprocess.run(['python', 'code/county-forecasts.py'])

# Daily Pulls - Power Plants
subprocess.run(['python', 'code/facility-forecasts.py'])

###############################################################################


###############################################################################
# Update GitHub

my_msg = "Daily update: " + str(date.today())

subprocess.run(['git', 'add', '.'], cwd=repo_path)
subprocess.run(['git', 'commit', '-m', my_msg], cwd = repo_path)
subprocess.run(['git', 'push'], cwd = repo_path)

###############################################################################


###############################################################################
# Send Email Update

OBS_NUM_COUNTIES = pd.read_csv(repo_path + 'reference-data/daily-obs-counties.csv')
OBS_NUM_COUNTIES = OBS_NUM_COUNTIES['num'][0]
OBS_NUM_PLANTS = pd.read_csv(repo_path + 'reference-data/daily-obs-facilities.csv')
OBS_NUM_PLANTS = OBS_NUM_PLANTS['num'][0]

subject = "Daily Weather Forecast Data"
body = "The daily weather forecast data pull has finished for the day. There were " \
    + str(OBS_NUM_COUNTIES) + " observations in the county data and " + \
    str(OBS_NUM_PLANTS) + " observations in the plant data." 
sender = "evan.perry.personal@gmail.com"
recipients = ["evan.perry.personal@gmail.com"]
password = API_KEY

def send_email(subject, body, sender, recipients, password):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
       smtp_server.login(sender, password)
       smtp_server.sendmail(sender, recipients, msg.as_string())
    print("Message sent.")

send_email(subject, body, sender, recipients, password)

os.remove(repo_path + 'reference-data/daily-obs-counties.csv')
os.remove(repo_path + 'reference-data/daily-obs-facilities.csv')

###############################################################################