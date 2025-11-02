from paddleocr import PaddleOCR
from pathlib import Path
from app.config import OCR_LANG, OUTPUT_DIRS

# ---------- SETUP ----------
# Ensure OCR output directory exists
Path(OUTPUT_DIRS["ocr_outputs"]).mkdir(parents=True, exist_ok=True)

# Initialize OCR model once at import
print(f"[🧠 Initializing PaddleOCR] Language: {OCR_LANG}")
ocr = PaddleOCR(lang=OCR_LANG, use_angle_cls=True, show_log=False)


# ---------- MAIN FUNCTION ----------
def run_ocr(image_path, save_output=True):
    """
    Run OCR on a given image file path using PaddleOCR.
    Returns extracted text as a single string.
    Optionally saves text to outputs/ocr_outputs/.
    """
    try:
        print(f"[📸 Running OCR on]: {image_path}")
        result = ocr.ocr(image_path, cls=True)

        extracted_text = []
        for line in result:
            for word_info in line:
                text_segment = word_info[1][0].strip()
                if text_segment:
                    extracted_text.append(text_segment)

        final_text = "\n".join(extracted_text).strip()

        if not final_text:
            print("[⚠️ No text detected]")
            return ""

        # Optionally save extracted text
        if save_output:
            output_file = OUTPUT_DIRS["ocr_outputs"] / f"ocr_result_{Path(image_path).stem}.txt"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(final_text)
            print(f"[✅ OCR Text Saved]: {output_file}")

        print(f"[🧾 Extracted OCR Text]: {final_text[:250]}{'...' if len(final_text) > 250 else ''}")
        return final_text

    except Exception as e:
        print(f"[❌ OCR Error]: {e}")
        return ""
