#!/usr/bin/env bash

# Set up logging
LOG_FILE="/var/log/speedtest.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Log HA server address
echo "[$TIMESTAMP] HA server address: $HA_SERVER" >> $LOG_FILE

echo "[$TIMESTAMP] Starting speedtest..." >> $LOG_FILE

# Run the speedtest script
/usr/local/bin/python /app/speedtest-cli-2ha.py >> $LOG_FILE 2>&1

# Log the completion
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
echo "[$TIMESTAMP] Speedtest completed" >> $LOG_FILE
echo "----------------------------------------" >> $LOG_FILE
