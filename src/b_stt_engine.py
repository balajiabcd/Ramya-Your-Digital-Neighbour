import logging
import tempfile
import os
from typing import Any, Optional

logger = logging.getLogger(__name__)

_stt_engine: Optional['STTEngine'] = None

def get_stt_engine() -> 'STTEngine':
    global _stt_engine
    if _stt_engine is None:
        _stt_engine = STTEngine()
    return _stt_engine

class STTEngine:
    model: Any
    
    def __init__(self) -> None:
        self.model = None
        self._load_model()
    
    def _load_model(self) -> None:
        try:
            from faster_whisper import WhisperModel
            logger.info("Loading Whisper model (base, English only)...")
            self.model = WhisperModel("base", device="cpu", compute_type="int8")
            logger.info("Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise RuntimeError(f"STT model failed to load: {e}")
    
    def transcribe(self, audio_data: bytes) -> str:
        if not self.model:
            raise RuntimeError("STT model not loaded")
        
        if not audio_data or len(audio_data) < 1000:
            return ""
        
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as tmp:
                tmp.write(audio_data)
                tmp_path = tmp.name
            
            try:
                segments, info = self.model.transcribe(
                    tmp_path,
                    language="en",
                    beam_size=1,
                    vad_filter=True,
                    vad_parameters=dict(min_silence_duration_ms=500)
                )
                
                text = " ".join([seg.text for seg in segments]).strip()
                logger.info(f"Transcription: {text}")
                return text
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
            
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            raise
