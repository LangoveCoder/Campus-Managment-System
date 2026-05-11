def format_cnic(raw):
    """Convert 13-digit raw CNIC to XXXXX-XXXXXXX-X format."""
    digits = ''.join(filter(str.isdigit, str(raw)))
    if len(digits) == 13:
        return f"{digits[:5]}-{digits[5:12]}-{digits[12]}"
    return raw
