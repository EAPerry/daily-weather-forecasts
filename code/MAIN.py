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
from git import Repo
from git import Actor

###############################################################################


# Daily Pulls - Counties
subprocess.run(['python', 'county-forecasts.py'])

# Daily Pulls - Power Plants
subprocess.run(['python', 'facility-forecasts.py'])

# Update GitHub
repo_path = 'C:/Users/eaper/OneDrive/personal-website/daily-weather-forecasts'
os.chdir(repo_path)

repo = Repo.init(repo_path).git
index = Repo.init(repo_path).index

committer = Actor("EAPerry", "eaperry36@gmail.com")

index.add(['README.md'])
index.commit('Test commit')

















subprocess.Popen(
    ['C:/Program Files/Git/git-bash.exe', 'C:/Users/eaper/OneDrive/personal-website/daily-weather-forecasts/code/commit-to-github.sh']
    
    
    
    )
