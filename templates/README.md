# Templates Folder - Frontend Documentation

## Overview

The `templates/` folder contains all HTML templates for the Ramya AI chatbot application. These templates define the user interface that users interact with when using the application.

---

## Folder Structure

```
templates/
├── login.html      # Login and registration page
├── home.html      # Main chat interface
└── index.html     # Landing/welcome page
```

---

## Templates

### 1. Login Page (`login.html`)

**Purpose:** User authentication interface

**Features:**
- Login form with username/password
- Registration form with username/password/email
- Tabbed interface to switch between login and register
- Real-time form validation
- Error/success message display
- Responsive design

**Form Fields:**
- Username (required, min 3 characters)
- Password (required, min 6 characters)
- Email (optional)

**JavaScript Features:**
- Tab switching between Login/Register
- AJAX form submission
- Error message display
- Automatic redirect on successful login

**Design:**
- Dark theme matching app aesthetic
- Card-based layout
- Smooth animations
- Brand logo and tagline

---

### 2. Home Page (`home.html`)

**Purpose:** Main chat interface for interacting with Ramya

**Features:**
- Chat message display area
- Message input field
- Voice input button (microphone)
- Voice output controls (play/pause)
- Chat history sidebar/panel
- New chat button
- Delete chat functionality

**Components:**
- **Header** - App name, user info, logout button
- **Sidebar** - Chat history list, new chat button
- **Chat Area** - Message display, timestamps
- **Input Area** - Text input, voice buttons, send button

**JavaScript Features:**
- Real-time message sending
- Stream response handling
- Voice recording (Web Speech API or MediaRecorder)
- Text-to-Speech playback
- Auto-scroll to latest message
- Chat history management (create, switch, delete)

**Styling:**
- Dark theme (#0f172a background)
- Message bubbles (user vs AI)
- Timestamps on messages
- Responsive design
- Smooth transitions

---

### 3. Index Page (`index.html`)

**Purpose:** Landing/welcome page

**Features:**
- Welcome message
- Call-to-action to login
- App branding and description

**Design:**
- Simple, clean layout
- Brand-focused
- Navigation to login

---

## Design System

### Color Palette

| Color | Hex | Usage |
|-------|-----|-------|
| Dark Background | #0f172a | Main background |
| Card Background | #1e293b | Cards, sidebars |
| Border | #334155 | Borders, dividers |
| Primary Text | #ffffff | Headings |
| Secondary Text | #94a3b8 | Descriptions |
| Accent Blue | #3b82f6 | Active states, links |
| Success Green | #22c55e | Success messages |
| Error Red | #ef4444 | Error messages |

### Typography

- **Font Family:** Inter (Google Fonts)
- **Headings:** 600 weight
- **Body:** 300-400 weight

### Layout

- **Container:** Centered card layout
- **Responsive:** Mobile-friendly
- **Animations:** Fade-in effects

---

## Integration with Backend

### Login Flow

1. User enters credentials
2. JavaScript sends POST to `/login`
3. Backend validates and creates session
4. On success, redirect to `/home`

### Registration Flow

1. User fills registration form
2. JavaScript sends POST to `/register`
3. Backend creates user with bcrypt password
4. Success message shown, switch to login tab

### Chat Flow

1. User types message or uses voice input
2. JavaScript sends POST to `/send_message`
3. Backend processes through AI engine
4. Response streamed back to UI
5. Messages displayed in chat area

### Voice Features

**Input (STT):**
1. User clicks microphone button
2. Audio recorded via Web Speech API
3. POST to `/stt` endpoint
4. Text returned and placed in input

**Output (TTS):**
1. AI response received
2. User clicks play button
3. POST to `/tts_stream` endpoint
4. Audio streamed and played

---

## Static Assets

Templates reference static files from `/static/`:

| File | Usage |
|------|-------|
| `global.css` | Common styles |
| `script.js` | Common JavaScript |
| `image.png` | App icon/logo |

---

## Security Considerations

- CSRF protection via Flask session
- XSS prevention (template auto-escaping)
- Secure cookie settings in production
- Input validation on backend

---

## Responsive Design

Templates are designed to work on:
- Desktop (1024px+)
- Tablet (768px - 1023px)
- Mobile (320px - 767px)

---

## Browser Support

- Chrome/Edge (recommended)
- Firefox
- Safari

---

## Customization

To modify the UI:

1. **Colors:** Edit CSS variables in each template
2. **Fonts:** Change Google Fonts import
3. **Layout:** Modify HTML structure and CSS
4. **Functionality:** Update JavaScript in `<script>` tags

---

## Dependencies

- **Google Fonts:** Inter
- **Flask:** Template rendering
- **Web Speech API:** Voice input (browser)
- **MediaRecorder API:** Voice recording

---

## Related Files

- `src/routes/k_auth.py` - Authentication endpoints
- `src/routes/m_chat.py` - Chat endpoints
- `src/routes/n_tts.py` - Text-to-Speech endpoints
- `src/routes/o_stt.py` - Speech-to-Text endpoints
- `static/script.js` - Frontend JavaScript
- `static/global.css` - Global styles

---

For more details, see the main project documentation.
