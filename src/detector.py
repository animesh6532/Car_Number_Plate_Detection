import cv2
import os
import urllib.request
import numpy as np
from PIL import Image

# OCR Libraries
try:
    import pytesseract
except ImportError:
    pytesseract = None

import easyocr

# =========================
# TESSERACT CONFIG (OPTIONAL BACKUP)
# =========================
TESSERACT_CMD_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

if pytesseract is not None and os.path.exists(TESSERACT_CMD_PATH):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD_PATH

# =========================
# MODEL CONFIG
# =========================
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MODEL_DIR = os.path.join(BASE_DIR, 'models')
MODEL_FILE = 'haarcascade_russian_plate_number.xml'
MODEL_PATH = os.path.join(MODEL_DIR, MODEL_FILE)

MODEL_URL = 'https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_russian_plate_number.xml'


class PlateDetector:
    def __init__(self):
        """Initialize detector and OCR"""
        self.load_model()
        self.cascade = cv2.CascadeClassifier(MODEL_PATH)

        # Initialize EasyOCR (Deep Learning OCR)
        self.reader = easyocr.Reader(['en'])

    # =========================
    # LOAD MODEL
    # =========================
    def load_model(self):
        if not os.path.exists(MODEL_DIR):
            os.makedirs(MODEL_DIR)

        if not os.path.exists(MODEL_PATH):
            print("Downloading Haar Cascade model...")
            urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
            print("Model downloaded.")
        else:
            print("Model already exists.")

    # =========================
    # DETECT PLATE (FIXED)
    # =========================
    def detect_plate(self, image):
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        plates = self.cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )

        return plates

    # =========================
    # DRAW BOX
    # =========================
    def draw_bounding_box(self, image, coordinates):
        img_copy = image.copy()

        for (x, y, w, h) in coordinates:
            cv2.rectangle(img_copy, (x, y), (x + w, y + h), (0, 255, 0), 3)
            cv2.putText(img_copy, "Plate", (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        return img_copy

    # =========================
    # EXTRACT REGION (FIXED 🔥)
    # =========================
    def extract_plate_region(self, image, coordinates):
        crops = []

        for (x, y, w, h) in coordinates:
            crop = image[y:y + h, x:x + w]

            h_crop, w_crop, _ = crop.shape

            # 🔥 Focus center area (remove logo like TATA)
            cropped_plate = crop[int(h_crop * 0.3):int(h_crop * 0.8), :]

            crops.append(cropped_plate)

        return crops

    # =========================
    # EASYOCR (IMPROVED 🔥)
    # =========================
    def extract_text_easyocr(self, img_crop):
        try:
            result = self.reader.readtext(img_crop)

            if not result:
                return "No text detected"

            # 🔥 Pick longest text (plate usually longest)
            text = max(result, key=lambda x: len(x[1]))[1]

            clean_text = ''.join(e for e in text if e.isalnum()).upper()

            return clean_text

        except Exception as e:
            print(f"EasyOCR Error: {e}")
            return "OCR failed"

    # =========================
    # OPTIONAL BACKUP OCR (TESSERACT)
    # =========================
    def extract_text_with_tesseract(self, img_crop):
        if pytesseract is None:
            return "OCR not available"

        try:
            gray = cv2.cvtColor(img_crop, cv2.COLOR_BGR2GRAY)
            gray = cv2.resize(gray, None, fx=3, fy=3)

            pil_img = Image.fromarray(gray)

            config = '--oem 3 --psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

            text = pytesseract.image_to_string(pil_img, config=config)
            clean_text = ''.join(e for e in text if e.isalnum()).upper()

            return clean_text.strip()

        except Exception:
            return "OCR failed"

    # =========================
    # FULL PIPELINE (UPDATED 🔥)
    # =========================
    def process_pipeline(self, image):
        plates = self.detect_plate(image)

        if len(plates) == 0:
            return image, None, "No plate detected"

        annotated_image = self.draw_bounding_box(image, plates)
        crops = self.extract_plate_region(image, plates)

        # Choose largest plate
        target_crop = crops[0]
        max_area = 0

        for i, (x, y, w, h) in enumerate(plates):
            area = w * h
            if area > max_area:
                max_area = area
                target_crop = crops[i]

        text = self.extract_text_easyocr(target_crop)

        if text == "No text detected" or text == "OCR failed":
            text = "Plate detected, text unclear"

        return annotated_image, target_crop, text


# =========================
# GLOBAL INSTANCE
# =========================
detector_instance = PlateDetector()
