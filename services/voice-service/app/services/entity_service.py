import re


def extract_amount(text: str):

    if not text:
        return None

    # matches: 500, 1000, 500 rupees, ₹500
    patterns = [
        r'₹\s?(\d+)',
        r'(\d+)\s?rupees',
        r'(\d+)\s?rs',
        r'(\d+)'
    ]

    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            return int(match.group(1))

    return None


def extract_recipient(text: str):

    if not text:
        return None

    # patterns for recipient name
    patterns = [
        r'to\s+([A-Za-z]+)',
        r'ko\s+([A-Za-z]+)',
        r'send\s+\d+\s+(?:rupees\s+)?to\s+([A-Za-z]+)',
        r'transfer\s+\d+\s+(?:rupees\s+)?to\s+([A-Za-z]+)'
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)

    return None


async def extract_entities(text: str):

    amount = extract_amount(text)
    recipient = extract_recipient(text)

    return {
        "amount": amount,
        "recipient": recipient
    }
