import shutil
import subprocess
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Import your app modules
from app.config import OUTPUT_DIRS, DEFAULT_LANGUAGE
from app.ocr import run_ocr
from app.voice import speech_to_text, text_to_speech, translate_text
from app.agent import initialize_agent, chat_completion, run_query

# Create FastAPI app
app = FastAPI(title="FarmGuide API", version="1.0")

# Allow CORS from React dev server (adjust origin if needed)
ALLOWED_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static folder to serve generated audio files
audio_dir = Path(OUTPUT_DIRS["voice_outputs"])
audio_dir.mkdir(parents=True, exist_ok=True)
app.mount("/audio", StaticFiles(directory=str(audio_dir)), name="audio")

# Allowed file extensions
ALLOWED_IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_AUDIO_EXT = {".wav", ".mp3", ".ogg", ".webm", ".m4a"}

# Initialize agent at startup (lazy initialize if it fails)
AGENT = None
try:
    AGENT = initialize_agent()
except Exception:
    AGENT = None


def save_upload(upload: UploadFile, dest_folder: Path) -> Path:
    """
    Save an UploadFile to the given folder and return the saved Path.
    """
    dest_folder.mkdir(parents=True, exist_ok=True)
    dest_path = dest_folder / upload.filename
    with open(dest_path, "wb") as f:
        shutil.copyfileobj(upload.file, f)
    return dest_path


def check_ffmpeg_available():
    """
    Check if ffmpeg is available on PATH.
    """
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False


def convert_to_wav(input_path: Path) -> Path:
    """
    Convert uploaded audio to WAV (mono, 16 kHz) using ffmpeg.
    If input is already WAV, return it directly.
    """
    if input_path.suffix.lower() == ".wav":
        return input_path

    if not check_ffmpeg_available():
        raise HTTPException(status_code=500, detail="ffmpeg is required to convert audio. Please install ffmpeg.")

    out_path = input_path.with_suffix(".wav")
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(input_path),
        "-ac", "1",
        "-ar", "16000",
        str(out_path),
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return out_path
    except subprocess.CalledProcessError:
        raise HTTPException(status_code=500, detail="Failed to convert audio to WAV.")


class QueryRequest(BaseModel):
    ocr_text: Optional[str] = ""
    farmer_query: Optional[str] = ""
    language: Optional[str] = DEFAULT_LANGUAGE


@app.post("/api/ocr")
async def endpoint_ocr(image: UploadFile = File(...)):
    """
    Upload an image and return OCR text.
    Accepts: jpg, jpeg, png, webp
    """
    suffix = Path(image.filename).suffix.lower()
    if suffix not in ALLOWED_IMAGE_EXT:
        raise HTTPException(status_code=400, detail="Unsupported image type. Allowed: JPG, PNG, WEBP.")

    try:
        saved = save_upload(image, OUTPUT_DIRS["ocr_outputs"])
        text = run_ocr(str(saved))
        return {"ocr_text": text, "saved_path": str(saved)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/stt")
async def endpoint_stt(audio: UploadFile = File(...), language: str = Form(DEFAULT_LANGUAGE)):
    """
    Upload audio and return transcript.
    Accepts: wav, mp3, ogg, webm, m4a
    """
    suffix = Path(audio.filename).suffix.lower()
    if suffix not in ALLOWED_AUDIO_EXT:
        raise HTTPException(status_code=400, detail="Unsupported audio type. Allowed: WAV, MP3, OGG, WEBM, M4A.")

    try:
        saved = save_upload(audio, OUTPUT_DIRS["recordings"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save audio: {e}")

    try:
        wav = convert_to_wav(saved)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audio conversion error: {e}")

    asr_result = speech_to_text(str(wav), language=language)
    if not asr_result:
        raise HTTPException(status_code=500, detail="Transcription failed.")
    return {"transcript": asr_result["text"], "language": asr_result["language"], "saved_path": str(saved)}


@app.post("/api/query")
async def endpoint_query(req: QueryRequest):
    """
    Send OCR text and farmer query to the agent.
    Returns agent text, translated text and audio URL (if TTS generated).
    """
    ocr_text = req.ocr_text or ""
    farmer_query = req.farmer_query or ""
    language = req.language or DEFAULT_LANGUAGE

    combined_input = f"OCR Text:\n{ocr_text}\n\nFarmer Query:\n{farmer_query}"

    # Prepare message for agent
    input_message = chat_completion(combined_input)

    global AGENT
    if AGENT is None:
        AGENT = initialize_agent()
        if AGENT is None:
            raise HTTPException(status_code=500, detail="Agent initialization failed.")

    try:
        agent_text = run_query(input_message, agent_executor=AGENT)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {e}")

    if not agent_text:
        agent_text = "No answer available."

    # Translate agent_text to user's language if needed
    translated = agent_text
    if language and language != "en":
        try:
            translated = translate_text(agent_text, source_lang="en", target_lang=language)
        except Exception:
            translated = agent_text

    # Generate TTS in requested language
    tts_path = None
    if translated and str(translated).strip():
        tts_path = text_to_speech(translated, language=language)

    audio_url = f"/audio/{Path(tts_path).name}" if tts_path else None

    return {"response": agent_text, "translated_response": translated, "audio_url": audio_url}


@app.post("/api/voice-query")
async def endpoint_voice_query(audio: UploadFile = File(...), language: str = Form(DEFAULT_LANGUAGE)):
    """
    Upload audio, run ASR, run agent, and return transcript + agent response + TTS audio URL.
    """
    suffix = Path(audio.filename).suffix.lower()
    if suffix not in ALLOWED_AUDIO_EXT:
        raise HTTPException(status_code=400, detail="Unsupported audio type.")

    try:
        saved = save_upload(audio, OUTPUT_DIRS["recordings"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save audio: {e}")

    try:
        wav = convert_to_wav(saved)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audio conversion error: {e}")

    asr_result = speech_to_text(str(wav), language=language)
    if not asr_result:
        raise HTTPException(status_code=500, detail="Transcription failed.")
    user_text = asr_result["text"]

    combined_input = f"OCR Text:\n\nFarmer Query:\n{user_text}"
    input_message = chat_completion(combined_input)

    global AGENT
    if AGENT is None:
        AGENT = initialize_agent()
        if AGENT is None:
            raise HTTPException(status_code=500, detail="Agent init failed.")

    try:
        agent_text = run_query(input_message, agent_executor=AGENT)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {e}")

    if not agent_text:
        agent_text = "No answer available."

    translated = agent_text
    if language and language != "en":
        try:
            translated = translate_text(agent_text, source_lang="en", target_lang=language)
        except Exception:
            translated = agent_text

    tts_path = None
    if translated and str(translated).strip():
        tts_path = text_to_speech(translated, language=language)

    audio_url = f"/audio/{Path(tts_path).name}" if tts_path else None

    return {
        "transcript": user_text,
        "response": agent_text,
        "translated_response": translated,
        "audio_url": audio_url,
    }


@app.get("/api/ping")
async def ping():
    return {"status": "ok"}


# Direct file serving for audio if needed (StaticFiles already mounted at /audio)
@app.get("/audio/{filename}")
async def get_audio_file(filename: str):
    file_path = audio_dir / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found.")
    return FileResponse(str(file_path), media_type="audio/mpeg")

