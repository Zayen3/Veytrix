from pathlib import Path

from PIL import Image, ExifTags, UnidentifiedImageError


def get_tag_value(exif_data, tag_name):
    """Return the value of a readable EXIF tag."""

    for tag_id, value in exif_data.items():
        readable_name = ExifTags.TAGS.get(tag_id, str(tag_id))

        if readable_name == tag_name:
            return value

    return None


def extract_metadata(file_path):
    """
    Open an image and extract basic file information
    along with important EXIF metadata.
    """

    file = Path(file_path)

    # Check whether the file exists
    if not file.is_file():
        raise FileNotFoundError(
            "File not found. Check the file path and try again."
        )

    try:
        with Image.open(file_path) as image:
            exif_data = image.getexif()

            return {
                "file_name": file.name,
                "format": image.format,
                "width": image.width,
                "height": image.height,
                "metadata_count": len(exif_data),
                "exif_data": exif_data,
                "make": get_tag_value(exif_data, "Make"),
                "model": get_tag_value(exif_data, "Model"),
                "software": get_tag_value(exif_data, "Software"),

                # Common EXIF timestamp fields
                "capture_date": get_tag_value(
                    exif_data, "DateTime"
                ),
                "original_date": get_tag_value(
                    exif_data, "DateTimeOriginal"
                ),
                "digitized_date": get_tag_value(
                    exif_data, "DateTimeDigitized"
                ),
            }

    except UnidentifiedImageError:
        raise ValueError(
            "Unsupported or invalid image file. "
            "Please provide a valid image."
        )

    except OSError as error:
        raise RuntimeError(
            f"Unable to read the image file: {error}"
        )