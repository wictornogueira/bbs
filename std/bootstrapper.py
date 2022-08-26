import os
import sys

BBS_DIR = os.path.dirname(os.path.abspath(__file__))
PLUGINS_DIR = os.path.join(BBS_DIR, "plugins")

# Add current directory to path

sys.path.append(BBS_DIR)
sys.path.append(os.path.join(BBS_DIR, "natives"))

# Create plugins directory

if not os.path.exists(PLUGINS_DIR):
  os.mkdir(PLUGINS_DIR)

# Run updater and load plugins

import updater
import loader
