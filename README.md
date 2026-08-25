# Veytrix

Veytrix is a Python-based metadata privacy tool that inspects image metadata, identifies potential privacy risks, and creates a cleaned copy with EXIF metadata removed.

## Features

- Extracts EXIF metadata from images
- Detects device manufacturer and model
- Detects camera or software information
- Extracts capture timestamps
- Detects embedded GPS metadata
- Converts GPS coordinates to decimal latitude and longitude
- Analyzes metadata for privacy risks
- Categorizes risks as High, Medium, or Low
- Provides a privacy risk breakdown
- Creates a cleaned copy without EXIF metadata
- Preserves the original image
- Verifies metadata removal after sanitization

## Privacy Risk Analysis

Veytrix categorizes detected metadata based on potential privacy impact.

### High Risk

- Precise GPS coordinates
- GPS metadata that may contain location information

### Medium Risk

- Device model information
- Capture timestamps

### Low Risk

- Device manufacturer information
- Camera or software metadata

## Project Structure

```text
Veytrix/
│
├── samples/
│   ├── test.jpeg
│   └── test_cleaned.jpeg
│
├── src/
│   ├── main.py
│   ├── metadata.py
│   ├── gps.py
│   ├── analyzer.py
│   └── sanitizer.py
│
├── requirements.txt
└── README.md
```

## Installation

Clone the repository:

```bash
git clone <repository-url>
cd Veytrix
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate the virtual environment.

### Windows PowerShell

```powershell
venv\Scripts\Activate.ps1
```

Install the required dependency:

```bash
pip install -r requirements.txt
```

## Usage

Run the application from the project root:

```bash
python src/main.py
```

Enter the path to an image when prompted:

```text
Enter the path of an image: samples\test.jpeg
```

Veytrix will inspect the image and generate a metadata privacy report.

Example:

```text
=======================================================
VEYTRIX - METADATA PRIVACY REPORT
=======================================================

FILE INFORMATION
File: test.jpeg
Format: JPEG
Dimensions: 3072 x 4080

METADATA FOUND
✓ Device Manufacturer: Xiaomi
✓ Device Model: 22120RN86I
✓ Software: MediaTek Camera Application
✓ Capture Date: 19 Aug 2026, 21:26:06
⚠ GPS Location Data: DETECTED
  Latitude: 12.887237° N
  Longitude: 77.581015° E

PRIVACY RISK ANALYSIS

HIGH RISK
⚠ Precise GPS coordinates are embedded in this image.

MEDIUM RISK
⚠ Device model can help identify the device used.
⚠ Capture timestamp reveals when the image was taken.

LOW RISK
• Device manufacturer metadata detected.
• Camera/software metadata detected.

SUMMARY
Metadata fields found: 17
Privacy-sensitive fields: 5
Risk Breakdown: 1 High | 2 Medium | 2 Low
Overall Privacy Risk: HIGH
=======================================================
```

After the report, Veytrix asks whether metadata should be removed.

```text
Do you want to remove metadata from this image? (y/n):
```

If `y` is selected, Veytrix creates a new cleaned copy while preserving the original image.

Example:

```text
VEYTRIX - METADATA SANITIZATION

Original file: test.jpeg
Cleaned file: test_cleaned.jpeg
Status: Cleaned copy created successfully.

--- SANITIZATION VERIFICATION ---
✓ Verification successful: No EXIF metadata found.
```

## How It Works

```text
Image
  ↓
Metadata Extraction
  ↓
GPS Detection and Coordinate Conversion
  ↓
Privacy Risk Analysis
  ↓
Privacy Report
  ↓
Optional Metadata Sanitization
  ↓
Cleaned Copy
  ↓
Verification
```

## Technologies Used

- Python
- Pillow
- EXIF Metadata Processing

## Current Limitations

- Currently focused on image files supported by Pillow
- Sanitization currently targets EXIF metadata
- Risk analysis is based on predefined metadata categories

## Future Improvements

- Support for additional file formats
- PDF metadata inspection and sanitization
- Document metadata analysis
- Batch file processing
- Improved metadata risk scoring
- Command-line arguments
- Exportable privacy reports

## Disclaimer

Veytrix is intended for educational and privacy-awareness purposes. Metadata structures can vary between file formats and applications, so users should independently verify sanitization results when handling sensitive files.