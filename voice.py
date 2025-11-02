# app/voice.py
"""
Speech utilities: ASR (Whisper), translation, and TTS (gTTS).
- Uses openai-whisper (lazy model load)
- Uses deep_translator for optional translation
- Uses gTTS for TTS; Sindhi falls back to Urdu if unsupported
"""

import os
import time
from pathlib import Path
from gtts import gTTS
from deep_translator import GoogleTranslator
import whisper  # ensure package openai-whisper is installed
from app.config import DEFAULT_LANGUAGE, WHISPER_MODEL, TTS_PREFIX, OUTPUT_DIRS

# Ensure output directories exist
Path(OUTPUT_DIRS["voice_outputs"]).mkdir(parents=True, exist_ok=True)

# Lazy-load Whisper model to avoid heavy import at module import in some environments
_WHISPER_MODEL = None


def _get_whisper_model():
    global _WHISPER_MODEL
    if _WHISPER_MODEL is None:
        print(f"[ASR] Loading Whisper model: {WHISPER_MODEL}")
        _WHISPER_MODEL = whisper.load_model(WHISPER_MODEL)
    return _WHISPER_MODEL


# Translation helper
def translate_text(text: str, source_lang: str, target_lang: str) -> str:
    """
    Translate text between languages using GoogleTranslator.
    If source == target, returns original.
    """
    try:
        if not text or source_lang == target_lang:
            return text or ""
        translator = GoogleTranslator(source=source_lang, target=target_lang)
        translated = translator.translate(text)
        print(f"[Translate] {source_lang} -> {target_lang}: {translated[:200]}")
        return translated
    except Exception as e:
        print(f"[Translate] Error: {e}")
        return text


# ASR: transcribe audio -> returns plain string (or None)
def transcribe_audio(audio_file_path: str, language: str = DEFAULT_LANGUAGE) -> str | None:
    """
    Transcribe an audio file using Whisper.
    Returns transcribed text (string) or None on failure.
    language should be 'en', 'ur', or 'sd' if supported by model.
    """
    try:
        model = _get_whisper_model()
        lang_map = {"en": "en", "ur": "ur", "sd": "sd"}
        lang_code = lang_map.get(language, "en")
        print(f"[ASR] Transcribing file: {audio_file_path} (lang={lang_code})")
        result = model.transcribe(audio_file_path, language=lang_code)
        text = result.get("text", "").strip()
        print(f"[ASR] Transcript (first 200 chars): {text[:200]}")
        return text
    except Exception as e:
        print(f"[ASR] Error: {e}")
        return None


# Normalize punctuation for Urdu/Sindhi
def _clean_local_punctuation(text: str, lang: str) -> str:
    if not text:
        return ""
    if lang in ("ur", "sd"):
        replacements = {",": "،", ".": "۔", "?": "؟", "!": "!"}
        for eng, loc in replacements.items():
            text = text.replace(eng, loc)
    return text.strip()


# TTS: generate mp3 path (returns str path or None)
def text_to_speech(text: str, language: str = DEFAULT_LANGUAGE, filename_prefix: str = TTS_PREFIX) -> str | None:
    """
    Convert text to speech using gTTS.
    Sindhi falls back to Urdu for TTS playback if not supported.
    Returns path to generated mp3 or None.
    """
    try:
        if not text or not str(text).strip():
            print("[TTS] Empty text provided, skipping TTS.")
            return None

        # Determine gTTS language code; fallback for Sindhi
        available = None
        try:
            # tts_langs only available in newer gTTS; wrap in try
            from gtts.lang import tts_langs
            available = tts_langs()
        except Exception:
            available = {}

        requested = language if language in ("en", "ur") else "ur"
        if available and requested not in available:
            print(f"[TTS] Language '{language}' not supported by gTTS, falling back to 'ur'")
            requested = "ur"

        out_dir = Path(OUTPUT_DIRS["voice_outputs"])
        out_dir.mkdir(parents=True, exist_ok=True)
        timestamp = int(time.time())
        filename = f"{filename_prefix}_{requested}_{timestamp}.mp3"
        out_path = out_dir / filename

        text = _clean_local_punctuation(text, language)
        print(f"[TTS] Generating TTS (lang={requested}) -> {out_path}")
        tts = gTTS(text=text, lang=requested, slow=False)
        tts.save(str(out_path))
        print(f"[TTS] Saved: {out_path}")
        return str(out_path)
    except Exception as e:
        print(f"[TTS] Error: {e}")
        return None

