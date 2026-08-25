from PIL import ExifTags


def convert_to_degrees(value):
    """Convert GPS coordinates from degrees/minutes/seconds to decimal degrees."""

    try:
        degrees = float(value[0])
        minutes = float(value[1])
        seconds = float(value[2])

        return degrees + (minutes / 60) + (seconds / 3600)

    except (TypeError, ValueError, IndexError, ZeroDivisionError):
        return None


def check_gps_data(exif_data):
    """Check whether a GPS metadata section is present."""

    try:
        gps_data = exif_data.get_ifd(ExifTags.IFD.GPSInfo)
        return bool(gps_data)
    except Exception:
        return False


def extract_gps_coordinates(exif_data):
    """
    Extract GPS latitude and longitude from EXIF metadata.
    Returns None if usable coordinates are not available.
    """

    try:
        gps_data = exif_data.get_ifd(ExifTags.IFD.GPSInfo)

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

        latitude_ref = str(latitude_ref).upper()
        longitude_ref = str(longitude_ref).upper()

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

    except Exception:
        return None