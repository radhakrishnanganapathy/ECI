import os
import regex as re
import pandas as pd
import pytesseract
from pdf2image import convert_from_path
from PIL import Image

# ----------------------------
# CONFIGURATION
# ----------------------------

PDF_PATH = "2026-EROLLGEN-S22-73-SIR-DraftRoll-Revision1-TAM-291-WI.pdf"          # Input PDF
IMG_DIR = "images"              # Temp image folder
OUTPUT_CSV = "output.csv"       # Output file

DPI = 300

# Change this path ONLY if Tesseract is not in PATH (Windows)
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

OCR_LANG = "tam+eng"

# ----------------------------
# REGEX PATTERNS
# ----------------------------

patterns = {
    "voter_id": re.compile(r"(IKU|LPN)\d+"),
    "name": re.compile(r"பெயர்\s*[:\-]\s*(.+)"),
    "relation": re.compile(r"(தந்தை|கணவர்)\s*பெயர்\s*[:\-]\s*(.+)"),
    "age": re.compile(r"வயது\s*[:\-]\s*(\d+)"),
    "gender": re.compile(r"பாலினம்\s*[:\-]\s*(\S+)"),
    "house_no": re.compile(r"வீட்டு\s*எண்\s*[:\-]\s*(\d+)")
}

# ----------------------------
# STEP 1: PDF → IMAGES
# ----------------------------

def pdf_to_images(pdf_path, img_dir):
    os.makedirs(img_dir, exist_ok=True)
    pages = convert_from_path(pdf_path, dpi=DPI)

    image_paths = []
    for i, page in enumerate(pages):
        img_path = f"{img_dir}/page_{i+1}.png"
        page.save(img_path, "PNG")
        image_paths.append(img_path)

    print(f"[✓] Converted {len(image_paths)} pages to images")
    return image_paths

# ----------------------------
# STEP 2: OCR IMAGE
# ----------------------------

def ocr_image(image_path):
    img = Image.open(image_path)
    text = pytesseract.image_to_string(
        img,
        lang=OCR_LANG,
        config="--psm 6"
    )
    return text

# ----------------------------
# STEP 3: EXTRACT VOTERS
# ----------------------------

import regex as re

def extract_voters(text):
    voters = []
    lines = [l.strip() for l in text.splitlines() if l.strip()]

    current = None

    for line in lines:

        # --- Detect voter ID ---
        vid = re.search(r"(IKU|LPN)\d+", line)
        if vid:
            if current:
                voters.append(current)

            current = {
                "voter_id": vid.group(),
                "age": None,
                "gender": None
            }
            continue

        if not current:
            continue

        # --- Extract age (number near 'வயது') ---
        if "வயது" in line:
            age = re.search(r"\d{2}", line)
            if age:
                current["age"] = age.group()

        # --- Extract gender ---
        if "பாலினம்" in line:
            if "பெண்" in line:
                current["gender"] = "பெண்"
            elif "ஆண்" in line:
                current["gender"] = "ஆண்"

    if current:
        voters.append(current)

    return voters


# ----------------------------
# MAIN PIPELINE
# ----------------------------

def main():
    print("[*] Starting voter extraction...")

    # images = pdf_to_images(PDF_PATH, IMG_DIR)
    images = sorted([
    os.path.join(IMG_DIR, f)
    for f in os.listdir(IMG_DIR)
    if f.endswith(".png")
])

    all_voters = []

    for img in images:
        print(f"[*] OCR processing: {img}")
        text = ocr_image(img)
        voters = extract_voters(text)
        all_voters.extend(voters)

    df = pd.DataFrame(all_voters)

    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")

    print(f"[✓] Extraction complete")
    print(f"[✓] Total voters extracted: {len(df)}")
    print(f"[✓] Saved to {OUTPUT_CSV}")

# ----------------------------
# ENTRY POINT
# ----------------------------

if __name__ == "__main__":
    main()
