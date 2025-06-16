import fitz  # PyMuPDF
import pytesseract
from pdf2image import convert_from_path
import os
from PIL import Image, ImageEnhance, ImageFilter

def preprocess_image(img: Image.Image, tesseract_lang: str) -> Image.Image:
    """
    Предобработка изображения перед OCR:
    - перевод в оттенки серого
    - повышение контрастности
    - бинаризация
    - коррекция наклона (deskew) через pytesseract OSD
    - усиление резкости
    """
    gray = img.convert("L")
    enhancer = ImageEnhance.Contrast(gray)
    img_enh = enhancer.enhance(2.0)
    img_bw = img_enh.point(lambda x: 0 if x < 128 else 255, mode='1')

    try:
        osd = pytesseract.image_to_osd(img_bw, lang=tesseract_lang)
        for line in osd.splitlines():
            if line.startswith("Rotate:"):
                angle = int(line.split(":")[1].strip())
                if angle != 0:
                    img_bw = img_bw.rotate(-angle, expand=True)
                break
    except Exception:
        pass  # игнорируем ошибки OSD

    img_final = img_bw.filter(ImageFilter.SHARPEN)
    return img_final

def extract_text(filepath: str, tesseract_lang: str) -> str:
    """
    Извлекает текст из PDF:
    - сначала PyMuPDF
    - если неудачно, используется OCR с предобработкой
    """
    try:
        doc = fitz.open(filepath)
        txt = ''
        for page in doc:
            page_text = page.get_text()
            if page_text:
                txt += page_text + '\n'
        if txt.strip():
            print(f"[INFO] Извлечён текст из PDF без OCR: {os.path.basename(filepath)}")
            return txt
    except Exception as e:
        print(f"[ERROR] Ошибка PyMuPDF при обработке {os.path.basename(filepath)}: {e}")

    print(f"[INFO] Переход к OCR: {os.path.basename(filepath)}")
    try:
        images = convert_from_path(filepath, dpi=300)
    except Exception as e:
        print(f"[ERROR] Ошибка преобразования PDF в изображения: {e}")
        return ""

    ocr_text = ''
    custom_config = r'--oem 1 --psm 6'

    for i, img in enumerate(images):
        try:
            preprocessed = preprocess_image(img, tesseract_lang)
            page_text = pytesseract.image_to_string(preprocessed, lang=tesseract_lang, config=custom_config)
        except Exception as e:
            print(f"[WARNING] Ошибка OCR на странице {i+1} ({os.path.basename(filepath)}): {e}")
            try:
                page_text = pytesseract.image_to_string(img, lang=tesseract_lang, config=custom_config)
            except Exception:
                page_text = ''
        ocr_text += page_text + '\n'

    txt_path = filepath + '.ocr.txt'
    try:
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(ocr_text)
    except Exception as e:
        print(f"[ERROR] Не удалось сохранить OCR-текст: {e}")

    print(f"[INFO] OCR завершён для {os.path.basename(filepath)}. Длина текста: {len(ocr_text)} символов")
    return ocr_text
