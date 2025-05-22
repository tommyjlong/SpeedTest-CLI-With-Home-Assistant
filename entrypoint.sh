#!/bin/sh

# Create log files
touch /var/log/cron.log
touch /var/log/speedtest.log

# Create the crontab file
echo "${CRON_SCHEDULE} /app/run-speedtest.sh >> /var/log/cron.log 2>&1" > /etc/cron.d/speedtest-cron
chmod 0644 /etc/cron.d/speedtest-cron

# Apply cron job
echo "Applying cron job..."
crontab /etc/cron.d/speedtest-cron

# Load the environment variables
printenv | grep -v "no_proxy" >> /etc/environment

# Start cron
echo "Starting cron..."
cron

# Follow both log files
echo "Starting log monitoring..."
tail -f /var/log/cron.log /var/log/speedtest.log

