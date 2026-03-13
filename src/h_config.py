import os

OPEN_ROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

ALLOWED_VOICES = [
    "en-US-JennyNeural",
    "en-US-GuyNeural", 
    "en-US-AriaNeural",
    "en-GB-SoniaNeural",
    "en-GB-RyanNeural",
    "en-AU-NatashaNeural",
    "en-AU-WilliamNeural",
    "en-IN-RaviNeural",
    "en-IN-AditiNeural"
]

AUDIO_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'audio')
os.makedirs(AUDIO_DIR, exist_ok=True)
