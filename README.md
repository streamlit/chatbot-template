# Hotel OS Telegram Bot

This is a comprehensive Telegram bot designed to act as a "Hotel Operating System". It assists with managing bookings, verifying payments via OCR, tracking expenses, and controlling room hardware (lights, AC) via MQTT.

The bot is built with Python, using `python-telegram-bot`, `FastAPI`, and `SQLAlchemy`. It's designed to be deployed as a container on Hugging Face Spaces.

## Features

- **AI Assistant**: Powered by Google Gemini for general-purpose questions.
- **Payment Verification**: Upload a payment slip image, and the bot uses Tesseract OCR to extract the customer name and amount, then matches it against an unpaid booking in the database.
- **Expense Tracking**: Add expenses via the Telegram Web App.
- **Hardware Control**: Control IoT devices (like lights and AC) using the MQTT protocol, either via commands or the Web App.
- **Daily Reports**: Get a summary of daily income and expenses with the `/daily_report` command.
- **Database**: Uses SQLite to store all data, with automatic daily backups sent to your Telegram.
- **Automated Deployment**: Automatically deploys to a configured Hugging Face Space on push to the `main` branch via GitHub Actions.

## Project Structure

```
/hotel-os-bot
├── .github/workflows/huggingface.yml  # GitHub Action for auto-deployment
├── app/                               # Main application source code
│   ├── __init__.py
│   ├── main.py                        # FastAPI app and Telegram bot logic
│   ├── config.py                      # Configuration and environment variables
│   ├── database.py                    # SQLAlchemy models and DB functions
│   ├── ocr.py                         # Tesseract OCR processing logic
│   └── mqtt.py                        # MQTT publishing logic
├── scripts/
│   └── backup_db.py                   # Script for daily DB backups
├── webapp/                            # Telegram Web App files
│   ├── index.html
│   ├── style.css
│   └── app.js
├── .gitignore
├── Dockerfile                         # Docker container definition for HF Spaces
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
└── start.sh                           # Container startup script
```

## Deployment Guide

Follow these steps to get your bot running on Hugging Face Spaces, with automated deployments from your GitHub repository.

### Step 1: Push to GitHub

1.  Create a new **private** repository on GitHub.
2.  In your local terminal, add the GitHub repository as a remote:
    ```bash
    git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
    git branch -M main
    ```
3.  Commit and push all the generated files:
    ```bash
    git add .
    git commit -m "Initial project setup"
    git push -u origin main
    ```

### Step 2: Create a Hugging Face Space

1.  Go to [Hugging Face](https://huggingface.co/new-space) and create a new **Space**.
2.  **Owner/Space name**: Choose a name for your project (e.g., `hotel-os-bot`).
3.  **License**: Select `mit` or another license.
4.  **Select the Space SDK**: Choose **Docker** and `Blank` template.
5.  **Space hardware**: The free `CPU basic` is sufficient to start.
6.  **Secrets**: You do not need to set secrets here initially if you are using the GitHub Action workflow, but you will need to add them later for the bot to run.
7.  Click **Create Space**. The initial build will likely fail, which is normal.

### Step 3: Configure GitHub Actions for Auto-Deployment

1.  **Get Hugging Face Token**: In Hugging Face, go to `Your Profile -> Settings -> Access Tokens`. Create a new token with the `write` role. Copy this token.
2.  **Add Secret to GitHub**: In your GitHub repository, go to `Settings -> Secrets and variables -> Actions`. Create a **New repository secret**:
    *   **Name**: `HF_TOKEN`
    *   **Value**: Paste the Hugging Face token you just copied.
3.  **Update Workflow File**: Open `.github/workflows/huggingface.yml` in your local project. Replace the placeholder `YOUR_HF_USERNAME` and `YOUR_HF_SPACE_NAME` with your actual HF username and Space name.
    ```yaml
    # ...
    env:
      HF_SPACE_GIT_REPO: "https://huggingface.co/spaces/your-hf-username/your-hf-space-name"
    run: |
      git remote add space "https://USER:${{ secrets.HF_TOKEN }}@huggingface.co/spaces/your-hf-username/your-hf-space-name"
      git push --force space main
    ```
4.  Commit and push this change. This will trigger the first deployment from GitHub Actions. You can monitor its progress in the "Actions" tab of your GitHub repository.

### Step 4: Configure Bot Secrets in Hugging Face Space

For your bot to run correctly, it needs its API keys. These **must** be set in the Hugging Face Space settings, not in your code.

1.  In your HF Space, go to the `Settings` tab.
2.  Scroll down to **Repository secrets** and click **New secret**.
3.  Add the following secrets one by one:

    *   `TELEGRAM_BOT_TOKEN`: Your token from BotFather.
    *   `TELEGRAM_USER_ID`: Your numeric Telegram user ID. You can get this from a bot like `@userinfobot`.
    *   `GEMINI_API_KEY`: Your API key for Google Gemini.
    *   `MQTT_BROKER`: (Optional) The address of your MQTT broker. Defaults to `broker.hivemq.com`.
    *   `MQTT_TOPIC_PREFIX`: (Optional) The base topic for your MQTT devices. Defaults to `hotel/room1`.

### Step 5: Update Web App URL and Final Test

1.  **Update URL**: Once your space is deployed, it will have a URL like `https://your-username-your-space-name.hf.space`. You need to put this URL into the `app/main.py` file.
    ```python
    # in app/main.py, inside start_command function
    web_app_button = KeyboardButton(
        "Open Hotel OS Web App",
        web_app=WebAppInfo(url=f"https://your-hf-username-your-hf-space-name.hf.space/static/index.html")
    )
    ```
    *Note: The URL should point to the static HTML file.* 

2.  Commit and push this final change. The GitHub Action will run again and deploy the updated code.
3.  **Test**: Open Telegram and talk to your bot. Use the `/start` command to see the Web App button and test all features.
