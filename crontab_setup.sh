#!/bin/bash

# Define script variables
SCRIPT_PATH="/var/www/traffic-bot/run_bots.py"
PYTHON_PATH="/usr/bin/python3"
CRON_SCHEDULE="*/15 * * * *"

# Function to set up the cronjob
setup_cronjob() {
    echo "🔧 Setting up Cronjob..."
    (crontab -l 2>/dev/null; echo "$CRON_SCHEDULE $PYTHON_PATH $SCRIPT_PATH") | crontab -
    echo "✅ Cronjob has been successfully set up!"
}

# Execute the setup function
setup_cronjob
