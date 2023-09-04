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
from git import Repo

###############################################################################


# Daily Pulls - Counties
subprocess.run(['python', 'county-forecasts.py'])

# Daily Pulls - Power Plants
subprocess.run(['python', 'facility-forecasts.py'])

# Update GitHub
repo_path = 'C:/Users/eaper/OneDrive/personal-website/daily-weather-forecasts'

























subprocess.Popen(
    ['C:/Program Files/Git/git-bash.exe', 'C:/Users/eaper/OneDrive/personal-website/daily-weather-forecasts/code/commit-to-github.sh']
    
    
    
    )
