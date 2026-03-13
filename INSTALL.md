# Install Guide - Ramya: Your Digital Neighbour

> Run your own AI chatbot locally with your own API key

---

## Prerequisites

1. **Docker Desktop** installed on your computer
   - Download from https://www.docker.com/products/docker-desktop
2. **OpenRouter API Key** (free)
   - Get one at https://openrouter.ai/

---

## Quick Setup (5 minutes)

### Step 1: Clone the Project

```bash
git clone https://github.com/balajiabcd/Ramya-Your-Digital-Neighbour.git
cd Ramya-Your-Digital-Neighbour
```

### Step 2: Get Your API Key

1. Go to https://openrouter.ai/
2. Sign up for a free account
3. Copy your API key from the dashboard

### Step 3: Configure Environment

```bash
# Copy the example environment file
cp .env.example .env
```

Open `.env` in any text editor and replace:
- `OPENROUTER_API_KEY` with your key
- `SECRET_KEY` with a secure random string

Generate a secret key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Step 4: Start the App

```bash
docker-compose up -d --build
```

### Step 5: Open in Browser

Visit: **http://localhost:8080**

---

## Creating an Account

1. Click **"Register"** on the login page
2. Enter a username and password (min 6 characters)
3. Click **"Register"**
4. Log in with your new account

---

## First-Time Chat

1. Click **"+ New Chat"** to start a conversation
2. Type a message and press Enter
3. Wait for Ramya's response (streaming in real-time)

---

## Troubleshooting

### Docker not running?
- Start Docker Desktop application
- Wait for it to show "Docker is running"

### Port already in use?
If port 8080 is busy, change it in `.env`:
```env
PORT=8081
```
Then access at http://localhost:8081

### API key error?
Make sure you copied the key correctly into `.env` (no extra spaces)

### Need help?
- Check Docker logs: `docker-compose logs -f ramya`
- Restart the app: `docker-compose restart ramya`

---

## Stopping the App

```bash
docker-compose down
```

Your data (chats, memories) is saved in Docker volumes and will persist when you restart.

---

## Updating to Latest Version

```bash
git pull origin main
docker-compose up -d --build
```

---

## What's Included

| Feature | Description |
|---------|-------------|
| **AI Chat** | 15+ free AI models via OpenRouter |
| **Memory** | Remembers past conversations |
| **Voice** | Text-to-speech & speech-to-text |
| **Multi-chat** | Multiple conversations per user |

---

## Need Help?

- Open an issue: https://github.com/balajiabcd/Ramya-Your-Digital-Neighbour/issues
- Check the full README: https://github.com/balajiabcd/Ramya-Your-Digital-Neighbour#readme

---

*Enjoy your digital neighbour!*
