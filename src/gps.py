from PIL import ExifTags


def _get_gps_data(exif_data):
    """Return the GPS EXIF IFD if present."""

    try:
        gps_data = exif_data.get_ifd(ExifTags.IFD.GPSInfo)

        if gps_data:
            return gps_data

    except (AttributeError, KeyError, TypeError, ValueError):
        pass

    return None


def _to_float(value):
    """Safely convert an EXIF numeric value to float."""

    try:
        return float(value)
    except (TypeError, ValueError, ZeroDivisionError):
        return None


def convert_to_degrees(value):
    """Convert GPS coordinates from degrees/minutes/seconds to decimal degrees."""

    try:
        if len(value) != 3:
            return None

        degrees = _to_float(value[0])
        minutes = _to_float(value[1])
        seconds = _to_float(value[2])

        if None in (degrees, minutes, seconds):
            return None

        return degrees + (minutes / 60) + (seconds / 3600)

    except (TypeError, IndexError):
        return None


def _normalize_reference(reference):
    """Normalize GPS direction references such as N, S, E, and W."""

    if isinstance(reference, bytes):
        reference = reference.decode(errors="ignore")

    return str(reference).strip().upper()


def check_gps_data(exif_data):
    """Check whether GPS metadata is present in the image."""

    gps_data = _get_gps_data(exif_data)

    if not gps_data:
        return False

    return bool(gps_data)


def extract_gps_coordinates(exif_data):
    """
    Extract GPS latitude and longitude from EXIF metadata.

    Returns None if usable coordinates are not available.
    """

    gps_data = _get_gps_data(exif_data)

    if not gps_data:
        return None

    latitude = gps_data.get(2)
    latitude_ref = gps_data.get(1)

    longitude = gps_data.get(4)
    longitude_ref = gps_data.get(3)

    if not all([latitude, latitude_ref, longitude, longitude_ref]):
        return None

    latitude_decimal = convert_to_degrees(latitude)
    longitude_decimal = convert_to_degrees(longitude)

    if latitude_decimal is None or longitude_decimal is None:
        return None

    latitude_ref = _normalize_reference(latitude_ref)
    longitude_ref = _normalize_reference(longitude_ref)

    if latitude_ref == "S":
        latitude_decimal = -latitude_decimal

    if longitude_ref == "W":
        longitude_decimal = -longitude_decimal

    return {
        "latitude": latitude_decimal,
        "longitude": longitude_decimal,
        "latitude_ref": latitude_ref,
        "longitude_ref": longitude_ref,
    }