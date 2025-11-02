from app import (run_ocr, 
                 speech_to_text, text_to_speech, 
                 initialize_agent, 
                 chat_completion, 
                 run_query, 
                 DEFAULT_LANGUAGE)

agent_executor = initialize_agent()

# Example: process an image
ocr_text = run_ocr("data/test_images/sample.jpg")

# Example: process voice
stt_result = speech_to_text("data/test_audio/sample.wav", language="ur")
user_query = stt_result['text'] if stt_result else ""

# Combine input
combined_input = f"OCR Text:\n{ocr_text}\n\nFarmer Query:\n{user_query}"

# Prepare agent input
input_message = chat_completion(combined_input)

# Run agent
run_query(input_message)

# Generate TTS
tts_file = text_to_speech("This is a test response", language="ur")
