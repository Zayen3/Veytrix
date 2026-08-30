# 🔍 Veytrix

### Image Metadata Privacy Analyzer

**Veytrix** is a Python-based privacy tool that analyzes metadata embedded in digital images, identifies potential privacy risks, and allows users to selectively remove sensitive EXIF information while preserving the original image.

## ✨ Features

- Extracts and analyzes EXIF metadata
- Detects GPS coordinates, device information, timestamps, and software metadata
- Converts GPS coordinates to decimal latitude and longitude
- Categorizes potential privacy risks as **High, Medium, or Low**
- Supports selective removal of sensitive metadata
- Supports complete EXIF metadata removal
- Creates a separate sanitized copy without modifying the original image
- Verifies metadata removal after processing

## 🛠️ Technologies

- Python
- Pillow (PIL)
- EXIF Metadata Processing

## 🚀 Installation & Usage

```bash
git clone https://github.com/Zayen3/Veytrix.git
cd Veytrix
pip install -r requirements.txt
python src/main.py