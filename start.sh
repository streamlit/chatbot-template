#!/bin/bash

# Start the cron service in the background
cron

# Add the cron job for database backup
# This runs the backup script every day at midnight
# The output is redirected to /proc/1/fd/1 (container's stdout) to be visible in `docker logs`
(crontab -l 2>/dev/null; echo "0 0 * * * /usr/local/bin/python /app/scripts/backup_db.py >> /proc/1/fd/1 2>&1") | crontab -

# Start the main application
# Use uvicorn to run the FastAPI app. The bot will run in a background thread.
echo "Starting FastAPI server and Telegram Bot..."
uvicorn app.main:app --host 0.0.0.0 --port 7860
