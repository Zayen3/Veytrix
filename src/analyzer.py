from datetime import datetime

from gps import check_gps_data, extract_gps_coordinates


def analyze_privacy(metadata):
    """Analyze metadata and determine privacy risks."""

    exif_data = metadata["exif_data"]

    make = metadata["make"]
    model = metadata["model"]
    software = metadata["software"]

    capture_date = metadata["capture_date"]
    original_date = metadata["original_date"]
    digitized_date = metadata["digitized_date"]

    gps_section_detected = check_gps_data(exif_data)
    gps_coordinates = extract_gps_coordinates(exif_data)

    # Check whether any timestamp information is present
    timestamp_detected = any([
        capture_date,
        original_date,
        digitized_date,
    ])

    # Categorize privacy-sensitive metadata
    high_risk_fields = 0
    medium_risk_fields = 0
    low_risk_fields = 0

    # HIGH RISK: GPS location
    if gps_coordinates or gps_section_detected:
        high_risk_fields += 1

    # MEDIUM RISK: Device identification and timestamps
    if model:
        medium_risk_fields += 1

    # Multiple timestamps count as one privacy category
    if timestamp_detected:
        medium_risk_fields += 1

    # LOW RISK: General device and software information
    if make:
        low_risk_fields += 1

    if software:
        low_risk_fields += 1

    sensitive_fields = (
        high_risk_fields
        + medium_risk_fields
        + low_risk_fields
    )

    # Determine overall privacy risk
    if high_risk_fields > 0:
        overall_risk = "HIGH"
    elif medium_risk_fields > 0:
        overall_risk = "MEDIUM"
    else:
        overall_risk = "LOW"

    return {
        "gps_section_detected": gps_section_detected,
        "gps_coordinates": gps_coordinates,
        "timestamp_detected": timestamp_detected,
        "high_risk_fields": high_risk_fields,
        "medium_risk_fields": medium_risk_fields,
        "low_risk_fields": low_risk_fields,
        "sensitive_fields": sensitive_fields,
        "overall_risk": overall_risk,
    }


def format_capture_date(capture_date):
    """Convert an EXIF date format into a readable format."""

    if not capture_date:
        return None

    try:
        date_object = datetime.strptime(
            str(capture_date),
            "%Y:%m:%d %H:%M:%S"
        )

        return date_object.strftime(
            "%d %b %Y, %H:%M:%S"
        )

    except (ValueError, TypeError):
        return capture_date


def print_privacy_report(metadata, analysis):
    """Print the Veytrix metadata privacy report."""

    make = metadata["make"]
    model = metadata["model"]
    software = metadata["software"]

    capture_date = metadata["capture_date"]
    original_date = metadata["original_date"]
    digitized_date = metadata["digitized_date"]

    gps_section_detected = analysis["gps_section_detected"]
    gps_coordinates = analysis["gps_coordinates"]

    print("\n" + "=" * 55)
    print("VEYTRIX - METADATA PRIVACY REPORT")
    print("=" * 55)

    # FILE INFORMATION
    print("\nFILE INFORMATION")
    print(f"File: {metadata['file_name']}")
    print(f"Format: {metadata['format']}")
    print(f"Dimensions: {metadata['width']} x {metadata['height']}")

    # METADATA FOUND
    print("\nMETADATA FOUND")

    if make:
        print(f"✓ Device Manufacturer: {make}")

    if model:
        print(f"✓ Device Model: {model}")

    if software:
        print(f"✓ Software: {software}")

    # Display all detected timestamps
    formatted_capture_date = format_capture_date(capture_date)
    formatted_original_date = format_capture_date(original_date)
    formatted_digitized_date = format_capture_date(digitized_date)

    if formatted_capture_date:
        print(f"✓ Date Modified: {formatted_capture_date}")

    if formatted_original_date:
        print(f"✓ Date Taken: {formatted_original_date}")

    if formatted_digitized_date:
        print(f"✓ Date Digitized: {formatted_digitized_date}")

    # GPS information
    if gps_coordinates:
        print("⚠ GPS Location Data: DETECTED")
        print(
            f"  Latitude: {gps_coordinates['latitude']:.6f}° "
            f"{gps_coordinates['latitude_ref']}"
        )
        print(
            f"  Longitude: {gps_coordinates['longitude']:.6f}° "
            f"{gps_coordinates['longitude_ref']}"
        )

    elif gps_section_detected:
        print("⚠ GPS Metadata Section: DETECTED")
        print("  Precise coordinates could not be extracted.")

    else:
        print("✓ GPS Location Data: Not detected")

    # PRIVACY RISK ANALYSIS
    print("\nPRIVACY RISK ANALYSIS")

    if analysis["high_risk_fields"] > 0:
        print("\nHIGH RISK")

        if gps_coordinates:
            print("⚠ Precise GPS coordinates are embedded in this image.")
        else:
            print(
                "⚠ GPS metadata is present and may contain "
                "location information."
            )

    medium_risks = []

    if model:
        medium_risks.append(
            "⚠ Device model can help identify the device used."
        )

    if analysis["timestamp_detected"]:
        medium_risks.append(
            "⚠ Timestamp metadata can reveal when the image was "
            "taken, modified, or digitized."
        )

    if medium_risks:
        print("\nMEDIUM RISK")

        for risk in medium_risks:
            print(risk)

    low_risks = []

    if make:
        low_risks.append(
            "• Device manufacturer metadata detected."
        )

    if software:
        low_risks.append(
            "• Camera/software metadata detected."
        )

    if low_risks:
        print("\nLOW RISK")

        for risk in low_risks:
            print(risk)

    # SUMMARY
    print("\nSUMMARY")
    print(f"Metadata fields found: {metadata['metadata_count']}")
    print(
        f"Privacy-sensitive fields: "
        f"{analysis['sensitive_fields']}"
    )
    print(
        f"Risk Breakdown: "
        f"{analysis['high_risk_fields']} High | "
        f"{analysis['medium_risk_fields']} Medium | "
        f"{analysis['low_risk_fields']} Low"
    )
    print(f"Overall Privacy Risk: {analysis['overall_risk']}")
    print("=" * 55)