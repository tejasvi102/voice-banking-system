import random

BANK_HANDLE = "voicebank"


def generate_upi_options(name: str = None, email: str = None, phone: str = None):

    options = []

    if name:
        username = name.lower().replace(" ", "")
        options.append(f"{username}@{BANK_HANDLE}")
        options.append(f"{username}{random.randint(100,999)}@{BANK_HANDLE}")

    if email:
        email_prefix = email.split("@")[0]
        options.append(f"{email_prefix}@{BANK_HANDLE}")

    if phone:
        options.append(f"{phone}@{BANK_HANDLE}")

    # Remove duplicates
    return list(set(options))