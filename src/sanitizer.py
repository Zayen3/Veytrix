from pathlib import Path

from PIL import Image, ExifTags


def sanitize_image(file_path):
    """
    Create a cleaned copy of an image without EXIF metadata.

    The original file is never modified.
    """

    try:
        with Image.open(file_path) as image:
            cleaned_image = image.copy()

        original_path = Path(file_path)

        cleaned_path = original_path.with_name(
            f"{original_path.stem}_cleaned{original_path.suffix}"
        )

        # Save the copied image without passing original EXIF metadata
        cleaned_image.save(cleaned_path)

        return cleaned_path

    except FileNotFoundError:
        raise FileNotFoundError(
            "File not found. Check the file path and try again."
        )

    except Exception as error:
        raise RuntimeError(
            f"Error while sanitizing the file: {error}"
        )


def remove_gps_data(file_path):
    """
    Create a copy of an image with GPS metadata removed
    while preserving other EXIF metadata.
    """

    try:
        with Image.open(file_path) as image:
            exif_data = image.getexif()

            # Remove the GPS metadata section
            if ExifTags.IFD.GPSInfo in exif_data:
                del exif_data[ExifTags.IFD.GPSInfo]

            cleaned_image = image.copy()

            original_path = Path(file_path)

            cleaned_path = original_path.with_name(
                f"{original_path.stem}_no_gps{original_path.suffix}"
            )

            cleaned_image.save(
                cleaned_path,
                exif=exif_data.tobytes()
            )

        return cleaned_path

    except FileNotFoundError:
        raise FileNotFoundError(
            "File not found. Check the file path and try again."
        )

    except Exception as error:
        raise RuntimeError(
            f"Error while removing GPS data: {error}"
        )


def remove_device_data(file_path):
    """
    Create a copy of an image with device manufacturer and
    model information removed while preserving other EXIF metadata.
    """

    try:
        with Image.open(file_path) as image:
            exif_data = image.getexif()

            # EXIF tags for device manufacturer and model
            device_tags = [271, 272]

            for tag in device_tags:
                if tag in exif_data:
                    del exif_data[tag]

            cleaned_image = image.copy()

            original_path = Path(file_path)

            cleaned_path = original_path.with_name(
                f"{original_path.stem}_no_device{original_path.suffix}"
            )

            cleaned_image.save(
                cleaned_path,
                exif=exif_data.tobytes()
            )

        return cleaned_path

    except FileNotFoundError:
        raise FileNotFoundError(
            "File not found. Check the file path and try again."
        )

    except Exception as error:
        raise RuntimeError(
            f"Error while removing device data: {error}"
        )


def remove_timestamp_data(file_path):
    """
    Create a copy of an image with common EXIF timestamp
    information removed while preserving other EXIF metadata.
    """

    try:
        with Image.open(file_path) as image:
            exif_data = image.getexif()

            # Common EXIF timestamp tags
            timestamp_tags = [
                306,    # DateTime
                36867,  # DateTimeOriginal
                36868,  # DateTimeDigitized
            ]

            for tag in timestamp_tags:
                if tag in exif_data:
                    del exif_data[tag]

            cleaned_image = image.copy()

            original_path = Path(file_path)

            cleaned_path = original_path.with_name(
                f"{original_path.stem}_no_timestamp"
                f"{original_path.suffix}"
            )

            cleaned_image.save(
                cleaned_path,
                exif=exif_data.tobytes()
            )

        return cleaned_path

    except FileNotFoundError:
        raise FileNotFoundError(
            "File not found. Check the file path and try again."
        )

    except Exception as error:
        raise RuntimeError(
            f"Error while removing timestamp data: {error}"
        )


def remove_software_data(file_path):
    """
    Create a copy of an image with software metadata removed
    while preserving other EXIF metadata.
    """

    try:
        with Image.open(file_path) as image:
            exif_data = image.getexif()

            # EXIF tag for Software
            software_tag = 305

            if software_tag in exif_data:
                del exif_data[software_tag]

            cleaned_image = image.copy()

            original_path = Path(file_path)

            cleaned_path = original_path.with_name(
                f"{original_path.stem}_no_software"
                f"{original_path.suffix}"
            )

            cleaned_image.save(
                cleaned_path,
                exif=exif_data.tobytes()
            )

        return cleaned_path

    except FileNotFoundError:
        raise FileNotFoundError(
            "File not found. Check the file path and try again."
        )

    except Exception as error:
        raise RuntimeError(
            f"Error while removing software data: {error}"
        )


def verify_sanitization(cleaned_path):
    """
    Verify whether EXIF metadata was removed from the cleaned image.
    """

    try:
        with Image.open(cleaned_path) as cleaned_image:
            cleaned_exif = cleaned_image.getexif()

        return len(cleaned_exif) == 0

    except Exception as error:
        raise RuntimeError(
            f"Error while verifying sanitization: {error}"
        )