import pytest
from PIL import Image
from src.processors.ocr import preprocess_image

def test_preprocess_image_returns_image():
    img = Image.new("RGB", (100, 100), color="white")
    processed = preprocess_image(img, "eng")
    assert processed.mode == "1" or processed.mode == "L"

def test_preprocess_image_different_sizes():
    # Test small image
    img_small = Image.new("RGB", (50, 50), color="white")
    processed_small = preprocess_image(img_small, "eng")
    assert processed_small.mode == "1" or processed_small.mode == "L"
    
    # Test large image
    img_large = Image.new("RGB", (1000, 1000), color="white")
    processed_large = preprocess_image(img_large, "eng")
    assert processed_large.mode == "1" or processed_large.mode == "L"

def test_preprocess_image_different_colors():
    # Test black image
    img_black = Image.new("RGB", (100, 100), color="black")
    processed_black = preprocess_image(img_black, "eng")
    assert processed_black.mode == "1" or processed_black.mode == "L"
    
    # Test gray image
    img_gray = Image.new("RGB", (100, 100), color=(128, 128, 128))
    processed_gray = preprocess_image(img_gray, "eng")
    assert processed_gray.mode == "1" or processed_gray.mode == "L"

def test_preprocess_image_different_languages():
    img = Image.new("RGB", (100, 100), color="white")
    
    # Test English
    processed_eng = preprocess_image(img, "eng")
    assert processed_eng.mode == "1" or processed_eng.mode == "L"
    
    # Test Russian
    processed_rus = preprocess_image(img, "rus")
    assert processed_rus.mode == "1" or processed_rus.mode == "L"
    
    # Test combined language
    processed_eng_rus = preprocess_image(img, "eng+rus")
    assert processed_eng_rus.mode == "1" or processed_eng_rus.mode == "L"

def test_preprocess_image_grayscale_input():
    # Test with grayscale image
    img_gray = Image.new("L", (100, 100), color=128)
    processed = preprocess_image(img_gray, "eng")
    assert processed.mode == "1" or processed.mode == "L"

def test_preprocess_image_binary_input():
    # Test with binary image
    img_binary = Image.new("1", (100, 100), color=1)
    processed = preprocess_image(img_binary, "eng")
    assert processed.mode == "1" or processed.mode == "L"

def test_preprocess_image_rectangular():
    # Test rectangular image
    img_rect = Image.new("RGB", (200, 100), color="white")
    processed = preprocess_image(img_rect, "eng")
    assert processed.mode == "1" or processed.mode == "L"

def test_preprocess_image_square():
    # Test square image
    img_square = Image.new("RGB", (100, 100), color="white")
    processed = preprocess_image(img_square, "eng")
    assert processed.mode == "1" or processed.mode == "L"

def test_preprocess_image_with_text_simulation():
    # Create an image that simulates text (alternating black and white pixels)
    img = Image.new("RGB", (100, 100), color="white")
    pixels = img.load()
    for i in range(0, 100, 10):
        for j in range(0, 100, 10):
            pixels[i, j] = (0, 0, 0)  # Black pixels to simulate text
    
    processed = preprocess_image(img, "eng")
    assert processed.mode == "1" or processed.mode == "L"
