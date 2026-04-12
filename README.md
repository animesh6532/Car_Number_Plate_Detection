# Number Plate Detection System (ANPR Lite)

Welcome to **ANPR Lite**, a premium, production-ready Automatic Number Plate Recognition (ANPR) web application. This platform offers seamless vehicle number plate detection combined with Optical Character Recognition (OCR), wrapped in a sleek, scalable Glassmorphism UI. You can upload local images or harness the power of your webcam for live tracking!

![ANPR UI Demo Placeholder](https://via.placeholder.com/800x400?text=ANPR+Lite+Premium+Screenshot)

## 🎯 Features

- **Image Upload:** Upload vehicle images directly; the backend locates the number plate and crops it.
- **Live Webcam:** Access the system via device camera using WebRTC APIs & process frames on demand.
- **Computer Vision:** Employs OpenCV hardware-accelerated Haar Cascades to detect Russian format and generic number plates automatically.
- **Optical Character Recognition (OCR):** Integrates Tesseract to extract and digitise characters from the detected plate.
- **Premium Design:** Features a dark mode, glassmorphism interface styled purely with minimal CSS and fluid animations.
- **Graceful Fallbacks:** The pipeline supports environments without Tesseract by switching back elegantly.

## 📁 Folder Structure

```
number_plate_web_app/
│
├── app.py                   # Main Flask backend application core
├── requirements.txt         # Python dependency libraries list
├── README.md                # Project documentation
│
├── models/
│   └── haarcascade_...xml   # Downloaded Automatically! (Haar Cascade Weights)
│
├── static/
│   ├── uploads/             # Raw user uploaded images
│   ├── outputs/             # Images containing bounding boxes
│   └── styles.css           # Vanilla CSS implementing Glassmorphism
│
├── templates/
│   ├── index.html           # Homepage containing dynamic fallback upload forms
│   └── camera.html          # WebRTC integrated interface
│
└── src/
    └── detector.py          # OpenCV logic separating backend from logic pipeline
```

## 🚀 Installation & Setup

### 1. Prerequisites
Ensure you have Python 3.8+ installed on your system.

### 2. Install Tesseract OCR (Crucial for Text Extraction)
* **Windows:**
  - Download the [Tesseract installer for Windows](https://github.com/UB-Mannheim/tesseract/wiki).
  - Install it (usually to `C:\Program Files\Tesseract-OCR\`).
  - *Note:* Our system checks this default Windows path automatically, meaning no environment variables tweaking is technically necessary for a standard install!
* **Linux (Ubuntu/Debian):**
  - Run `sudo apt install tesseract-ocr`

### 3. Setup Python Virtual Environment (Optional but Recommended)
```bash
# Navigate to the project directory
cd number_plate_web_app

# Create a virtual environment
python -m venv venv

# Activate it (Windows)
venv\Scripts\activate
# Activate it (Mac/Linux)
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Run the Application
Start the Flask development server:
```bash
python app.py
```
Then, open your web browser and navigate to: `http://127.0.0.1:5000/`

## 🧪 Error Handling
- **Missing OpenCV Models:** The system downloads `haarcascade_russian_plate_number.xml` upon initialization automatically.
- **Tesseract Absent:** If Tesseract isn't installed locally, the backend catches the error and issues a UI warning instead of crashing.
- **Camera Permissions:** The browser handles hardware natively natively providing an alert if blocked.

## 📄 License
This project is open-source and free to be adapted for educational or enterprise applications.

---
*Built with ❤️ utilizing Python, OpenCV and Flask.*
