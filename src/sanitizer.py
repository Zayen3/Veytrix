from pathlib import Path
from PIL import Image


# =========================================================
# OUTPUT PATH
# =========================================================

def get_unique_output_path(original_path, suffix_label):
    """
    Generate a unique output path without overwriting an
    existing file.
    """

    original_path = Path(original_path)

    output_path = original_path.with_name(
        f"{original_path.stem}_{suffix_label}{original_path.suffix}"
    )

    counter = 1

    while output_path.exists():
        output_path = original_path.with_name(
            f"{original_path.stem}_{suffix_label}_{counter}"
            f"{original_path.suffix}"
        )
        counter += 1

    return output_path


# =========================================================
# INTERNAL HELPERS
# =========================================================

def _prepare_paths(file_path, output_path, suffix_label):
    """
    Convert paths to Path objects and generate an output path
    if one was not provided.
    """

    source = Path(file_path)

    if not source.exists():
        raise FileNotFoundError(
            "File not found. Check the file path and try again."
        )

    if output_path is None:
        output_path = get_unique_output_path(source, suffix_label)
    else:
        output_path = Path(output_path)

        # Never overwrite an existing file accidentally.
        if output_path.exists():
            output_path = get_unique_output_path(
                source,
                suffix_label
            )

    return source, output_path


def _save_with_exif(image, exif_data, output_path):
    """
    Save an image while preserving the supplied EXIF metadata.
    """

    image.save(
        output_path,
        exif=exif_data.tobytes()
    )


# =========================================================
# FULL EXIF SANITIZATION
# =========================================================

def sanitize_image(file_path, output_path=None):
    """
    Create a cleaned copy of an image without EXIF metadata.

    The original file is never modified.
    """

    source, output_path = _prepare_paths(
        file_path,
        output_path,
        "cleaned"
    )

    try:
        with Image.open(source) as image:

            # Load pixel data before the source file closes.
            image.load()

            cleaned_image = image.copy()

            # Remove EXIF metadata completely.
            cleaned_image.info.pop("exif", None)

            cleaned_image.save(output_path)

        return output_path

    except Exception as error:
        raise RuntimeError(
            f"Error while sanitizing the file: {error}"
        )


# =========================================================
# GPS REMOVAL
# =========================================================

def remove_gps_data(file_path, output_path=None):
    """
    Create a copy with GPS metadata removed while preserving
    other available EXIF metadata.
    """

    source, output_path = _prepare_paths(
        file_path,
        output_path,
        "no_gps"
    )

    try:
        with Image.open(source) as image:

            image.load()
            exif_data = image.getexif()

            # GPSInfo EXIF tag is 34853.
            gps_tag = 34853

            if gps_tag in exif_data:
                del exif_data[gps_tag]

            cleaned_image = image.copy()

            _save_with_exif(
                cleaned_image,
                exif_data,
                output_path
            )

        return output_path

    except Exception as error:
        raise RuntimeError(
            f"Error while removing GPS data: {error}"
        )


# =========================================================
# DEVICE INFORMATION REMOVAL
# =========================================================

def remove_device_data(file_path, output_path=None):
    """
    Remove common camera and device identity information while
    preserving other EXIF metadata.
    """

    source, output_path = _prepare_paths(
        file_path,
        output_path,
        "no_device"
    )

    try:
        with Image.open(source) as image:

            image.load()
            exif_data = image.getexif()

            # Make, Model
            device_tags = [
                271,
                272,
            ]

            for tag in device_tags:
                if tag in exif_data:
                    del exif_data[tag]

            cleaned_image = image.copy()

            _save_with_exif(
                cleaned_image,
                exif_data,
                output_path
            )

        return output_path

    except Exception as error:
        raise RuntimeError(
            f"Error while removing device data: {error}"
        )


# =========================================================
# TIMESTAMP REMOVAL
# =========================================================

def remove_timestamp_data(file_path, output_path=None):
    """
    Remove common timestamp information while preserving other
    EXIF metadata.
    """

    source, output_path = _prepare_paths(
        file_path,
        output_path,
        "no_timestamp"
    )

    try:
        with Image.open(source) as image:

            image.load()
            exif_data = image.getexif()

            # DateTime, DateTimeOriginal, DateTimeDigitized
            timestamp_tags = [
                306,
                36867,
                36868,
            ]

            for tag in timestamp_tags:
                if tag in exif_data:
                    del exif_data[tag]

            cleaned_image = image.copy()

            _save_with_exif(
                cleaned_image,
                exif_data,
                output_path
            )

        return output_path

    except Exception as error:
        raise RuntimeError(
            f"Error while removing timestamp data: {error}"
        )


# =========================================================
# SOFTWARE INFORMATION REMOVAL
# =========================================================

def remove_software_data(file_path, output_path=None):
    """
    Remove software/application metadata while preserving other
    EXIF metadata.
    """

    source, output_path = _prepare_paths(
        file_path,
        output_path,
        "no_software"
    )

    try:
        with Image.open(source) as image:

            image.load()
            exif_data = image.getexif()

            # Software EXIF tag
            software_tag = 305

            if software_tag in exif_data:
                del exif_data[software_tag]

            cleaned_image = image.copy()

            _save_with_exif(
                cleaned_image,
                exif_data,
                output_path
            )

        return output_path

    except Exception as error:
        raise RuntimeError(
            f"Error while removing software data: {error}"
        )


# =========================================================
# SANITIZATION VERIFICATION
# =========================================================

def verify_sanitization(cleaned_path, option="all"):
    """
    Verify that the selected metadata category was removed.

    For a full clean, verifies that no EXIF metadata remains.
    """

    cleaned_path = Path(cleaned_path)

    if not cleaned_path.exists():
        raise FileNotFoundError(
            "The sanitized output file could not be found."
        )

    try:
        with Image.open(cleaned_path) as image:

            exif_data = image.getexif()

            # Full EXIF removal
            if option == "all":
                return len(exif_data) == 0

            # GPS
            if option == "gps":
                return 34853 not in exif_data

            # Device manufacturer and model
            if option == "device":
                return (
                    271 not in exif_data
                    and 272 not in exif_data
                )

            # Timestamps
            if option == "timestamp":
                timestamp_tags = [306, 36867, 36868]

                return all(
                    tag not in exif_data
                    for tag in timestamp_tags
                )

            # Software
            if option == "software":
                return 305 not in exif_data

            return False

    except Exception as error:
        raise RuntimeError(
            f"Error while verifying sanitization: {error}"
        )


# Backward-compatible alias in case older code uses this name.
def verify_sanitization_old(cleaned_path):
    return verify_sanitization(cleaned_path, "all")