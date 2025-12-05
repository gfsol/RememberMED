# Telegram Medication Reminder Bot

This project implements a Telegram bot built with Flask that helps users manage medication reminders and retrieve drug information from the OpenFDA API. It includes a Premium subscription system and stores user and reminder data using SQLite.

## Features

- Interactive Telegram bot interface using custom keyboards
- Set medication reminders with dosage and time intervals
- Retrieve and translate medication information from OpenFDA
- View and delete active reminders
- Premium user system with extended features
- Integration with SQLite for persistent storage
- Docker support for containerized deployment

## Project Structure

```
.
├── app.py                # Main Flask application and Telegram bot logic
├── BBDD.py               # Database manager using SQLite3
├── app_db.db             # SQLite database file
├── Dockerfile            # Docker image definition
├── README.md             # Project documentation
├── requirements.txt      # Python dependencies (required for Docker build)
```

## Endpoints

- `/` — Main page with form to send a welcome message
- `/telegram` — Telegram webhook endpoint for processing bot commands and replies
- `/premium` — Page for submitting and processing payment data (mock)
- `/start` — API endpoint to manually create a new user

## How It Works

- Users interact with the bot using Telegram commands such as `/start`.
- Users can:
  - Set reminders with dosage, frequency, and start time
  - Get translated drug info using OpenFDA API
  - View or delete reminders
- Premium users can store unlimited reminders.
- Payments are simulated through a form that collects card data (no real processing).

## Database Schema

SQLite tables:

- `Usuario`: Stores user info, including premium status
- `Recordatorio`: Stores medication reminders
- `DosisProgramada`: Stores individual doses for each reminder
- `CuentaBancaria`: Stores fake card data for premium accounts

## Docker Deployment

You can deploy this bot using Docker and ngrok. Follow these steps:

### 1. Build Docker image

```bash
docker build -t telegram-bot .
```

### 2. Run Docker container

```bash
docker run -d -p 2001:5000 --name telegram-bot-container telegram-bot
```

### 3. Access the container and run ngrok

```bash
docker exec -it telegram-bot-container /bin/bash
ngrok http 5000
```

### 4. Set the Telegram Webhook

```bash
curl -F "url=https://<NGROK_URL>/telegram?token=<TELEGRAM_TOKEN>" https://api.telegram.org/bot<TELEGRAM_TOKEN>/setWebhook
```

## Notes

- The bot uses Markdown for Telegram messages.
- All reminder times are based on a 24-hour format (HH:MM).
- Webhook integration depends on `ngrok` for public access.

## Requirements

- Python 3.8+
- Flask
- requests
- schedule
- googletrans==4.0.0-rc1
- SQLite3 (built-in)

## License

This project is for educational purposes and is provided as-is, without warranty or production-grade security. Do not use real credit card data in forms.


# Bot Operation Guide

## Required Data to Operate the Bot

### Telegram Bot Token
1. **Register on Telegram**: Create an account if you don’t already have one.
2. **Add @BotFather**: Search and add @BotFather to your contacts.

### Create a Bot:
1. In the chat with @BotFather, type `/start`.
2. Then type `/newbot`.
3. Provide a name for the bot (any descriptive name).
4. Provide a unique username ending in `bot` (e.g., `medicobot`).
5. @BotFather will return a token like `123456789:Ab1cDef2GH`. Save it securely.

### Telegram User ID
1. **Add @userinfobot**: Search and start a chat with @userinfobot.
2. Type `/start` and get your Telegram user ID. Save it for later use.

---

## Environment Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

2. Activate the virtual environment:
   - **Windows**:
     ```bash
     venv\Scripts\activate
     ```
   - **macOS/Linux**:
     ```bash
     source venv/bin/activate
     ```

### Install dependencies
Inside the virtual environment:

```bash
pip install Flask requests pyngrok googletrans==4.0.0-rc1 schedule
```

---

## Ngrok Configuration

Ngrok is used to expose the local server to the public internet so Telegram can access it.

### Install ngrok
1. **Download ngrok**:
   - From: https://ngrok.com/download
   - Or via command:
     - **Windows**:
       ```bash
       choco install ngrok
       ```
     - **Linux/macOS**:
       ```bash
       brew install ngrok/ngrok/ngrok
       ```

2. **Authenticate ngrok**:
   - Register at ngrok and get your auth token.
   - Run:
     ```bash
     ngrok config add-authtoken YOUR_NGROK_TOKEN
     ```

3. **Run ngrok**:
   ```bash
   ngrok http 5000
   ```

   - Copy the generated public URL (e.g., `https://randomstring.ngrok.io`).
   - Set the Telegram webhook:
     ```bash
     curl -F "url=<NGROK_URL>/telegram?token=<TELEGRAM_TOKEN>" https://api.telegram.org/bot<TELEGRAM_TOKEN>/setWebhook
     ```

---

## Run the Web Application

1. Start Flask:
   ```bash
   python app.py
   ```

2. Open `http://127.0.0.1:5000/` locally or use the ngrok public URL.

3. **Access the Web Interface**:
   - Enter:
     - **Telegram Bot Token**
     - **Telegram Chat ID**
   - Click **Start Conversation** to begin interacting with the bot.

---

## Conclusion

By following these steps, you'll have a fully functional system that:
- Connects to Telegram
- Uses ngrok for public exposure
- Allows web interaction with the Telegram bot

