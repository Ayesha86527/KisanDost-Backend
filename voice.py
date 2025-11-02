import time
from pathlib import Path
from gtts import gTTS
from deep_translator import GoogleTranslator
import whisper
from app.config import DEFAULT_LANGUAGE, WHISPER_MODEL, TTS_PREFIX, OUTPUT_DIRS

# Ensure output directories exist
Path(OUTPUT_DIRS["voice_outputs"]).mkdir(parents=True, exist_ok=True)

# ---------- TRANSLATION ----------
def translate_text(text, source_lang, target_lang):
    """
    Translate text between English, Urdu, and Sindhi using GoogleTranslator.
    If source and target are the same, returns the original text.
    """
    try:
        if not text:
            return ""
        if source_lang == target_lang:
            return text
        translator = GoogleTranslator(source=source_lang, target=target_lang)
        translated = translator.translate(text)
        print(f"[📝 Translation] {source_lang} → {target_lang}: {translated}")
        return translated
    except Exception as e:
        print(f"[❌ Translation Error]: {e}")
        return text


# ---------- SPEECH-TO-TEXT (ASR) ----------
def speech_to_text(audio_file_path, language=DEFAULT_LANGUAGE):
    """
    Convert speech to text using Whisper.
    Supports English (en), Urdu (ur), and Sindhi (sd).
    """
    lang_map = {"en": "en", "ur": "ur", "sd": "sd"}
    try:
        print(f"[🎤 Whisper] Transcribing audio ({language})...")
        model = whisper.load_model(WHISPER_MODEL)
        result = model.transcribe(audio_file_path, language=lang_map.get(language, "en"))
        transcript = result.get("text", "").strip()
        print(f"[✅ ASR Transcript]: {transcript}")
        return {"text": transcript, "language": language}
    except Exception as e:
        print(f"[❌ ASR Error]: {e}")
        return None


# ---------- CLEAN TEXT FOR URDU/SINDHI ----------
def clean_text_urdu_sindhi(text, lang):
    """
    Normalize punctuation for Urdu and Sindhi outputs.
    """
    if lang in ["ur", "sd"]:
        replacements = {",": "،", ".": "۔", "?": "؟", "!": "!"}
        for eng, local in replacements.items():
            text = text.replace(eng, local)
    return text.strip()


# ---------- TEXT-TO-SPEECH (TTS) ----------
def text_to_speech(text, language=DEFAULT_LANGUAGE, filename_prefix=TTS_PREFIX):
    """
    Generate voice output using gTTS.
    Sindhi falls back to Urdu (gTTS doesn't support Sindhi natively).
    Returns path to generated .mp3 file.
    """
    gtts_lang = {"en": "en", "ur": "ur", "sd": "ur"}.get(language, "en")
    text = clean_text_urdu_sindhi(text, language)
    timestamp = int(time.time())
    output_path = OUTPUT_DIRS["voice_outputs"] / f"{filename_prefix}_{language}_{timestamp}.mp3"

    try:
        if not text.strip():
            print("[⚠️ TTS Warning] Empty text, skipping audio generation.")
            return None

        print(f"[🔊 TTS] Generating voice in {language.upper()}...")
        tts = gTTS(text=text, lang=gtts_lang, slow=False)
        tts.save(str(output_path))
        print(f"[✅ TTS Saved]: {output_path}")
        return str(output_path)
    except Exception as e:
        print(f"[❌ TTS Error]: {e}")
        return None


# ---------- PIPELINE HELPER (OPTIONAL) ----------
def process_voice_pipeline(audio_file_path, language=DEFAULT_LANGUAGE):
    """
    End-to-end pipeline:
    1. Speech-to-text (ASR)
    2. Translation (if needed)
    3. Text-to-speech (TTS)
    Returns both transcript and generated voice path.
    """
    asr_result = speech_to_text(audio_file_path, language)
    if not asr_result:
        return None

    transcript = asr_result["text"]
    translated_text = translate_text(transcript, source_lang=language, target_lang=DEFAULT_LANGUAGE)
    tts_path = text_to_speech(translated_text, language=language)
    
    return {
        "transcript": transcript,
        "translated": translated_text,
        "tts_path": tts_path
    }
