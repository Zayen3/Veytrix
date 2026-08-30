Veytrix

Veytrix is a Python-based metadata privacy tool that inspects image metadata, identifies potential privacy risks, and allows users to selectively remove sensitive EXIF metadata while preserving the original image.

Features
Extracts EXIF metadata from images
Detects device manufacturer and model information
Detects camera or software metadata
Detects common image timestamps
Detects embedded GPS metadata
Extracts and converts GPS coordinates to decimal latitude and longitude
Analyzes metadata for potential privacy risks
Categorizes risks as High, Medium, or Low
Provides a privacy risk breakdown
Supports selective metadata sanitization:
GPS location data
Device information
Timestamp information
Software information
Supports complete EXIF metadata removal
Creates a separate cleaned copy without modifying the original image
Verifies sanitization after processing
Privacy Risk Analysis

Veytrix categorizes detected metadata based on its potential privacy impact.

High Risk
Precise GPS coordinates
GPS metadata that may contain location information
Medium Risk
Device model information
Timestamp information that may reveal when an image was taken or processed
Low Risk
Device manufacturer information
Camera or software metadata
Project Structure
Veytrix/
│
├── samples/
│   └── test.jpeg
│
├── src/
│   ├── main.py
│   ├── metadata.py
│   ├── gps.py
│   ├── analyzer.py
│   └── sanitizer.py
│
├── requirements.txt
├── .gitignore
└── README.md

Sanitized images are generated as separate files in the same directory as the original image.

Installation

Clone the repository:

git clone <repository-url>
cd Veytrix

Create a virtual environment:

python -m venv venv

Activate the virtual environment.

Windows PowerShell
venv\Scripts\Activate.ps1

Install the required dependencies:

pip install -r requirements.txt
Usage

Run the application from the project root:

python src/main.py

Enter the path to an image when prompted:

Enter the path of an image: samples/test.jpeg

Veytrix will inspect the image and generate a metadata privacy report containing detected metadata, GPS information, and a privacy risk assessment.

After the report, select a sanitization option:

SANITIZATION OPTIONS
1. Remove GPS location data only
2. Remove device information only
3. Remove timestamp information only
4. Remove software information only
5. Remove all EXIF metadata
6. Cancel

Veytrix creates a separate output file for each sanitization operation while preserving the original image.

Examples of generated filenames:

test_no_gps.jpeg
test_no_device.jpeg
test_no_timestamp.jpeg
test_no_software.jpeg
test_cleaned.jpeg

After sanitization, Veytrix verifies whether the selected metadata was successfully removed.

How It Works
Image
  ↓
Metadata Extraction
  ↓
GPS Detection and Coordinate Extraction
  ↓
Privacy Risk Analysis
  ↓
Metadata Privacy Report
  ↓
Selective or Full Sanitization
  ↓
Cleaned Copy
  ↓
Verification
Technologies Used
Python
Pillow
EXIF Metadata Processing
Current Limitations
Currently focused on image files supported by Pillow
Sanitization primarily targets EXIF metadata
Metadata structures can vary between image formats and applications
Risk analysis is based on predefined metadata categories and does not represent a comprehensive privacy assessment
Future Improvements
Support for additional file formats
PDF metadata inspection and sanitization
Document metadata analysis
Batch file processing
Command-line arguments
Exportable privacy reports
More detailed metadata detection and analysis
Disclaimer

Veytrix is intended for educational and privacy-awareness purposes. Metadata structures can vary between file formats and applications, so users should independently verify sanitization results when handling sensitive files.