from django.core.exceptions import ValidationError


def validate_license(image):
    """
    Custom validation for the driver's license upload field.
    Ensures the file is an image and not larger than 5MB.
    """
    # File size limit: 5MB (5 * 1024 * 1024 bytes)
    max_size = 5 * 1024 * 1024
    if image.size > max_size:
        raise ValidationError("File size should not exceed 5MB.")

    # File type check: only allow jpg, jpeg, or png
    if not image.name.endswith(('.jpg', '.jpeg', '.png')):
        raise ValidationError("Only image files (JPG, JPEG, PNG) are allowed.")
