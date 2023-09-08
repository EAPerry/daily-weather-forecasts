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
# Last Revised: 2023-09-04
# version = 1.0
# -----------------------------------------------------------------------------

###############################################################################
# Setup

import subprocess
import os
from datetime import date

repo_path = 'C:/Users/eaper/OneDrive/personal-website/daily-weather-forecasts'
os.chdir(repo_path)

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

