from .ocr import run_ocr
from .voice import speech_to_text, text_to_speech, translate_text
from .agent import initialize_agent, chat_completion, run_query, web_search_tool
from .config import LANGUAGES, DEFAULT_LANGUAGE, OUTPUT_DIRS, TTS_PREFIX, WHISPER_MODEL

