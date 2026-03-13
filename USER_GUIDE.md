# User Guide - Ramya: Your Digital Neighbour

> Your Digital Neighbour

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Login Page](#login-page)
3. [Home Page](#home-page)
4. [Chat Page](#chat-page)
5. [Voice Features](#voice-features)
6. [Chat Management](#chat-management)
7. [Security &amp; Privacy](#security--privacy)

---

## Getting Started

### Prerequisites

- A modern web browser (Chrome, Firefox, Edge, Safari)
- Microphone access (for voice features)
- An account (Register with Username, Password, and Email)

### Starting the App

1. Open your browser and navigate to `http://localhost:5000`
2. You will be redirected to the login page

---

## Login Page

**URL:** `/login`

### Features

| Feature                  | Description                                                  |
| ------------------------ | ------------------------------------------------------------ |
| **Brand Display**  | Shows app icon and "Ramya - Your Digital Neighbour" branding |
| **Username Input** | Text field to enter your name                                |
| **Login Button**   | Click to authenticate and access the app                     |
| **Footer Note**    | Indicates local login is enabled                             |

### How to Use

1. Click **"Register"** if you don't have an account.
2. Enter your Username, Password, and Email.
3. Once registered, enter your credentials on the login page.
4. Click **"Login"** to access the dashboard.

> **Note:** For security, passwords must be at least 6 characters.

---

## Home Page

**URL:** `/home` (after login)

### Features

| Feature                   | Description                                |
| ------------------------- | ------------------------------------------ |
| **Welcome Banner**  | Displays welcome message with your name    |
| **User Profile**    | Shows your avatar and name in the header; includes Security settings |
| **Security Link**    | Click to open the Change Password modal |
| **Logout Button**   | Click to sign out and return to login page |
| **New Chat Button** | Start a completely new conversation        |
| **Chat History**    | Lists all your previous chat sessions      |
| **Empty State**     | Message shown when no chats exist yet      |

### How to Use

1. **View Previous Chats:** All your past conversations are listed on the page
2. **Continue a Chat:** Click on any existing chat bar to resume that conversation
3. **Start New Chat:** Click the "+ New Chat" bar or button to begin fresh
4. **Delete a Chat:** Click the delete icon (trash) on any chat bar to remove it

### Navigation Flow

```
Login Page → Home Page → Chat Page
                 ↓              ↓
            Logout         Back to Home
```

---

## Chat Page

**URL:** `/chat_page` or `/chat`

### Features

| Feature                            | Description                                      |
| ---------------------------------- | ------------------------------------------------ |
| **Sidebar - Chat List**      | Shows all your active chats in the left sidebar  |
| **Sidebar - New Chat**       | Button to start a new conversation               |
| **Sidebar - Security**       | Link to update your password                     |
| **Sidebar - User Profile**   | Displays your name and avatar with logout option |
| **Header - Brand**           | Shows Ramya logo and tagline                     |
| **Header - Online Status**   | Indicates bot is online and ready                |
| **Header - Mute Button**     | Toggle voice output on/off                       |
| **Header - Voice Settings**  | Configure voice speed and pitch                  |
| **Chat Window**              | Displays conversation history                    |
| **Message Input**            | Type your message and press Enter or click send  |
| **Voice Input (Microphone)** | Hold to speak, release to send                   |
| **Stop Generation**          | Button to stop ongoing response                  |
| **Markdown Rendering**       | Supports bold, italic, code, lists, etc.         |
| **Streaming Responses**      | See AI responses appear in real-time             |

### How to Use

#### Sending Messages

1. Type your message in the input field at the bottom
2. Press **Enter** or click the **send button** (paper plane icon)
3. Wait for Ramya's response (streaming in real-time)
4. Responses support markdown formatting

#### Using Voice Input

1. Click and **hold** the microphone button
2. Speak your message clearly
3. **Release** the button to send
4. Your speech will be transcribed and sent automatically

#### Stopping Responses

- Click the **stop button** (square icon) that appears while Ramya is responding
- This stops the current response generation

#### Switching Chats

1. Click on any chat name in the left sidebar
2. The conversation loads instantly
3. Continue from where you left off

---

## Voice Features

### Text-to-Speech (TTS)

Ramya can read her responses aloud.

| Control                   | Location       | Function                           |
| ------------------------- | -------------- | ---------------------------------- |
| **Mute/Unmute**     | Header         | Toggle voice output on/off         |
| **Voice Settings**  | Header         | Configure voice options            |
| **Voice Selection** | Settings Panel | Choose from 4 voices               |
| **Speed Control**   | Settings Panel | Adjust speech rate (-50% to +100%) |
| **Pitch Control**   | Settings Panel | Adjust pitch (-20Hz to +20Hz)      |

### Available Voices

| Voice   | Accent          |
| ------- | --------------- |
| Jenny   | 🇺🇸 American   |
| Neerja  | 🇮🇳 Indian     |
| Sonia   | 🇬🇧 British    |
| Natasha | 🇦🇺 Australian |

### Speech-to-Text (STT)

Convert your voice to text:

1. Click and **hold** the microphone button
2. Speak your message
3. Release to send
4. Text is automatically transcribed using Whisper AI

---

## Chat Management

### Starting a New Chat

- Click **"+ Start New Chat"** in sidebar
- Or click **"New Chat"** on Home page
- A fresh conversation begins with no previous context

### Continuing a Chat

1. From Home: Click any chat bar
2. From Chat Page: Click chat name in sidebar

### Deleting a Chat

1. Hover over the chat bar in Home page
2. Click the **delete icon** (trash)
3. Chat is permanently removed

### Chat Memory

Ramya **remembers** past conversations:

- Uses ChromaDB vector database for semantic search
- Retrieves relevant past messages when responding
- Provides personalized responses based on history
- Each user's chats are completely isolated

---

## Security & Privacy

### Authentication

- Secure username/password based authentication
- Password management (Change Password feature)
- Session-based authentication (secure, httpOnly cookies)
- Protected routes require active login

### Data Isolation

- Each user's data is stored separately
- Chat collections are prefixed with user identifier
- No cross-user data access

### Input Protection

- HTML tags are stripped from inputs
- Prompt injection detection blocks malicious commands
- Rate limiting: 5 requests per 60 seconds

### Security Headers

- X-Content-Type-Options: nosniff
- X-Frame-Options: SAMEORIGIN
- X-XSS-Protection: enabled

---

## Troubleshooting

### Common Issues

| Issue                  | Solution                                     |
| ---------------------- | -------------------------------------------- |
| Login not working      | Clear browser cookies and try again          |
| Voice not playing      | Check mute button and browser audio settings |
| Microphone not working | Grant microphone permission in browser       |
| Slow responses         | Check internet connection                    |
| Chat not loading       | Refresh the page                             |

### Rate Limiting

If you see "You're chatting too fast" message:

- Wait 60 seconds before sending more messages
- This protects against abuse

### Error Messages

- **400:** Invalid request or injection detected
- **401:** Please log in
- **429:** Too many requests, wait a moment
- **500:** Internal error, try refreshing

---

## Quick Reference

| Action        | How                              |
| ------------- | -------------------------------- |
| Send message  | Type + Enter or click send       |
| Use voice     | Hold mic button, speak, release  |
| New chat      | Click "+ Start New Chat"         |
| Switch chat   | Click chat name in sidebar       |
| Delete chat   | Hover chat bar, click trash icon |
| Change voice  | Click gear icon, adjust settings |
| Mute/unmute   | Click speaker icon               |
| Stop response | Click stop button                |
| Change Password | Click "Security" link           |
| Logout        | Click logout link                |

---

*Built with care by the Ramya Bot Team*
