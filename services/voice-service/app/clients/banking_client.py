import requests

BANKING_CORE_URL = "http://localhost:8002"


def execute_upi_transfer(user_id, upi_id, amount):

    payload = {
        "from_user_id": user_id,
        "to_upi_id": upi_id,
        "amount": amount,
        "currency": "INR",
        "idempotency_key": f"voice-{user_id}-{amount}"
    }

    response = requests.post(
        f"{BANKING_CORE_URL}/transfer/execute",
        json=payload
    )

    return response.json()