import fitz
import pytesseract
from pdf2image import convert_from_path
from PIL import Image, ImageEnhance, ImageFilter
import os
import logging

def preprocess_image(img: Image.Image, tesseract_lang: str) -> Image.Image:
    """Preprocess an image for OCR, including grayscale, contrast, binarization, and rotation correction."""
    gray = img.convert("L")
    enhancer = ImageEnhance.Contrast(gray)
    img_enh = enhancer.enhance(2.0)
    img_bw = img_enh.point(lambda x: 0 if x < 128 else 255, mode="1")
    try:
        osd = pytesseract.image_to_osd(img_bw, lang=tesseract_lang)
        for line in osd.splitlines():
            if line.startswith("Rotate:"):
                angle = int(line.split(":")[1].strip())
                if angle != 0:
                    img_bw = img_bw.rotate(-angle, expand=True)
                break
    except Exception:
        pass
    return img_bw.filter(ImageFilter.SHARPEN)

def extract_text(filepath: str, tesseract_lang: str) -> str:
    """Extract text from a PDF file using PyMuPDF or OCR as fallback."""
    try:
        doc = fitz.open(filepath)
        txt = "".join(page.get_text() + "\n" for page in doc)
        if txt.strip():
            logging.info(f"Text extracted by PyMuPDF: {os.path.basename(filepath)}")
            return txt
    except Exception as e:
        logging.error(f"PyMuPDF error for {os.path.basename(filepath)}: {e}")

    logging.info(f"OCR fallback for {os.path.basename(filepath)}")
    try:
        images = convert_from_path(filepath, dpi=300)
    except Exception as e:
        logging.error(f"PDF→image conversion error: {e}")
        return ""

    ocr_text = ""
    config = "--oem 1 --psm 6"
    for i, img in enumerate(images):
        try:
            pre = preprocess_image(img, tesseract_lang)
            page = pytesseract.image_to_string(pre, lang=tesseract_lang, config=config)
        except Exception:
            page = pytesseract.image_to_string(img, lang=tesseract_lang, config=config)
        ocr_text += page + "\n"

    txt_path = filepath + ".ocr.txt"
    try:
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(ocr_text)
    except Exception as e:
        logging.error(f"Saving OCR text failed: {e}")

    logging.info(f"OCR done ({len(ocr_text)} chars)")
    return ocr_text
