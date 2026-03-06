from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.migrations.session import get_db
from app.models.account import Account
from app.models.upi_handle import UPIHandle
from app.utils.upi_qr import generate_upi_qr

router = APIRouter()


@router.get("/qr/{upi_id}")
def generate_qr(upi_id: str, db: Session = Depends(get_db)):

    upi = db.query(UPIHandle).filter(
        UPIHandle.upi_id == upi_id,
        UPIHandle.is_active == True
    ).first()

    if not upi:
        raise HTTPException(status_code=404, detail="UPI not found")

    account = db.query(Account).filter(
        Account.id == upi.account_id
    ).first()

    qr_data = generate_upi_qr(
        upi_id=upi.upi_id,
        name="User"
    )

    return {
        "status": "success",
        "data": qr_data
    }