import qrcode
from io import BytesIO
import base64


def generate_upi_qr(upi_id: str, name: str = "User"):

    upi_url = f"upi://pay?pa={upi_id}&pn={name}&cu=INR"

    qr = qrcode.make(upi_url)

    buffer = BytesIO()
    qr.save(buffer, format="PNG")

    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    return {
        "upi_url": upi_url,
        "qr_base64": qr_base64
    }