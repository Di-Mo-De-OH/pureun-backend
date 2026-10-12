def format_phone_number(phone_number: str) -> str:
    return f"{phone_number[:3]}-{phone_number[3:-4]}-{phone_number[-4:]}"
