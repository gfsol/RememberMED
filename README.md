# Telegram Medication Reminder Bot

This project implements a Telegram bot built with Flask that helps users manage medication reminders and retrieve drug information from the OpenFDA API. It includes a Premium subscription system and stores user and reminder data using SQLite.

---

# 1. Bot Operation Guide

## Required Data to Operate the Bot

### Telegram Bot Token
1. **Register on Telegram**: Create an account if you don’t already have one.
2. **Add @BotFather**: Search and add @BotFather to your contacts.
3. **Create a Bot**:
   - Type `/start`
   - Type `/newbot`
   - Provide a name (e.g., `Medication Bot`)
   - Provide a username ending in `bot` (e.g., `medicobot`)
   - Copy and save the access token (e.g., `123456789:Ab1cDef2GH`)

### Telegram User ID
1. **Add @userinfobot**: Start a chat with @userinfobot.
2. Type `/start` and copy your Telegram user ID.

---

# 2. Environment Setup

## Create and Activate Virtual Environment

```bash
python -m venv venv
```

- **Windows**:
  ```bash
  venv\Scripts\activate
  ```
- **macOS/Linux**:
  ```bash
  source venv/bin/activate
  ```

## Install Dependencies

```bash
pip install Flask requests pyngrok googletrans==4.0.0-rc1 schedule
```

---

# 3. Project Structure

```
.
├── app.py                # Main Flask application and Telegram bot logic
├── BBDD.py               # Database manager using SQLite3
├── app_db.db             # SQLite database file
├── Dockerfile            # Docker image definition
├── README.md             # Project documentation
├── requirements.txt      # Python dependencies (required for Docker build)
```

---

# 4. How It Works

- Users interact with the bot using Telegram commands such as `/start`.
- Users can:
  - Set reminders with dosage, frequency, and start time
  - Get translated drug info using OpenFDA API
  - View or delete reminders
- Premium users can store unlimited reminders.
- Payments are simulated through a form that collects card data (no real processing).

---

# 5. Application Endpoints

- `/` — Main page with form to send a welcome message
- `/telegram` — Telegram webhook endpoint for processing bot commands and replies
- `/premium` — Page for submitting and processing payment data (mock)
- `/start` — API endpoint to manually create a new user

---

# 6. Database Schema

SQLite tables:

- `Usuario`: Stores user info, including premium status
- `Recordatorio`: Stores medication reminders
- `DosisProgramada`: Stores individual doses for each reminder
- `CuentaBancaria`: Stores fake card data for premium accounts

---

# 7. Run the Web Application

1. Start Flask:
   ```bash
   python app.py
   ```

2. Open in browser:
   - Local: `http://127.0.0.1:5000/`
   - Public: ngrok URL

3. Access the Web Interface:
   - Enter your **Telegram Bot Token** and **Chat ID**
   - Click **Start Conversation**

---

# 8. Ngrok Configuration

Ngrok is used to expose the local server to the public internet so Telegram can access it.

## Install ngrok

- Download from: https://ngrok.com/download
- Or install with:
  - **Windows**:
    ```bash
    choco install ngrok
    ```
  - **Linux/macOS**:
    ```bash
    brew install ngrok/ngrok/ngrok
    ```

## Authenticate and Run

```bash
ngrok config add-authtoken YOUR_NGROK_TOKEN
ngrok http 5000
```

## Set Telegram Webhook

```bash
curl -F "url=<NGROK_URL>/telegram?token=<TELEGRAM_TOKEN>" https://api.telegram.org/bot<TELEGRAM_TOKEN>/setWebhook
```

---

# 9. Docker Deployment (Optional)

## Build Docker Image

```bash
docker build -t telegram-bot .
```

## Run Docker Container

```bash
docker run -d -p 2001:5000 --name telegram-bot-container telegram-bot
```

## Access and Expose with ngrok

```bash
docker exec -it telegram-bot-container /bin/bash
ngrok http 5000
```

---

# 10. Notes

- Bot uses Markdown to format Telegram messages
- Reminder times follow 24-hour format (HH:MM)
- Database uses SQLite (local file-based)
- Webhook integration requires a public URL via ngrok

---

# 11. Requirements

- Python 3.8+
- Flask
- requests
- schedule
- googletrans==4.0.0-rc1
- SQLite3 (built-in)

---

# 12. License

This project is for educational purposes and is provided as-is, without warranty or production-grade security. Do not use real credit card data in forms.
