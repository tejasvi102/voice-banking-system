from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.migrations.session import get_db
from app.services.account_service import get_account_by_user_id
from app.models.account import Account
from app.models.upi_handle import UPIHandle
from app.models.cards import Card
from app.utils.upi_generator import generate_upi_options
from app.schemas.account import AccountCreateRequest
from uuid import uuid4
from pydantic import BaseModel
from typing import Optional
from app.schemas.upi import ConfirmUPIRequest


router = APIRouter()


@router.post("/")
def create_account(
    request: AccountCreateRequest,
    db: Session = Depends(get_db)
):
    existing = db.query(Account).filter(
        Account.user_id == request.user_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Account already exists"
        )

    account = Account(
        user_id=request.user_id,
        balance=request.initial_balance,
        currency=request.currency,
        status="active"
    )

    db.add(account)
    db.commit()
    db.refresh(account)

    return {
        "status": "success",
        "data": {
            "user_id": str(account.user_id),
            "balance": str(account.balance),
            "currency": account.currency,
            "status": account.status
        },
        "error": None
    }



import httpx
from uuid import UUID

USER_SERVICE_URL = "http://localhost:8007"   # change if needed


@router.post("/{user_id}/suggest-upi")
def suggest_upi(user_id: str, db: Session = Depends(get_db)):

    # Validate UUID
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user_id")

    account = db.query(Account).filter(
        Account.user_id == user_uuid
    ).first()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    # Fetch user details from user-service
    try:
        response = httpx.get(f"{USER_SERVICE_URL}/{user_id}")
        response.raise_for_status()
        user_data = response.json()["data"]
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch user details"
        )

    name = user_data.get("name")
    email = user_data.get("email")
    phone = user_data.get("phone")

    options = generate_upi_options(
        name=name,
        email=email,
        phone=phone
    )

    return {
        "status": "success",
        "data": {
            "upi_options": options
        }
    }

@router.get("/upi/{upi_id}")
def resolve_upi(upi_id: str, db: Session = Depends(get_db)):

    upi = db.query(UPIHandle).filter(
        UPIHandle.upi_id == upi_id
    ).first()

    if not upi:
        raise HTTPException(status_code=404, detail="UPI ID not found")

    account = db.query(Account).filter(
        Account.id == upi.account_id
    ).first()

    return {
        "status": "success",
        "data": {
            "upi_id": upi.upi_id,
            "account_id": str(account.id),
            "user_id": str(account.user_id),
            "card_id": str(upi.card_id) if upi.card_id else None
        }
    }

from uuid import UUID

@router.post("/{user_id}/confirm-upi")
def confirm_upi(
    user_id: str,
    request: ConfirmUPIRequest,
    db: Session = Depends(get_db)
):
    # Validate user_id UUID
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user_id format")

    account = db.query(Account).filter(
        Account.user_id == user_uuid
    ).first()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    # Check global UPI uniqueness
    existing = db.query(UPIHandle).filter(
        UPIHandle.upi_id == request.upi_id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="UPI already taken")

    card = None

    # Optional card validation
    if request.card_id:

        try:
            card_uuid = UUID(str(request.card_id))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid card_id format")

        card = db.query(Card).filter(
            Card.id == card_uuid,
            Card.account_id == account.id,
            Card.is_active == True
        ).first()

        if not card:
            raise HTTPException(
                status_code=400,
                detail="Card not found or does not belong to account"
            )

    # If setting as primary → unset existing primary
    if request.is_primary:
        db.query(UPIHandle).filter(
            UPIHandle.account_id == account.id,
            UPIHandle.is_primary == True
        ).update({"is_primary": False})

    new_upi = UPIHandle(
        account_id=account.id,
        card_id=card.id if card else None,
        upi_id=request.upi_id,
        is_primary=request.is_primary
    )

    db.add(new_upi)
    db.commit()
    db.refresh(new_upi)

    return {
        "status": "success",
        "data": {
            "upi_id": new_upi.upi_id,
            "account_id": str(new_upi.account_id),
            "card_id": str(new_upi.card_id) if new_upi.card_id else None,
            "is_primary": new_upi.is_primary
        },
        "message": "UPI ID created successfully"
    }


@router.get("/upi/{upi_id}")
def get_account_by_upi(upi_id: str, db: Session = Depends(get_db)):

    upi = db.query(UPIHandle).filter(
        UPIHandle.upi_id == upi_id,
        UPIHandle.is_active == True
    ).first()

    if not upi:
        raise HTTPException(status_code=404, detail="UPI ID not found")

    account = db.query(Account).filter(
        Account.id == upi.account_id
    ).first()

    return {
        "status": "success",
        "data": {
            "user_id": str(account.user_id),
            "upi_id": upi.upi_id,
            "is_primary": upi.is_primary,
            "card_id": str(upi.card_id) if upi.card_id else None,
            "status": account.status
        }
    }

@router.get("/{user_id}/upi")
def list_user_upi(user_id: str, db: Session = Depends(get_db)):

    account = db.query(Account).filter(
        Account.user_id == user_id
    ).first()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    upis = db.query(UPIHandle).filter(
        UPIHandle.account_id == account.id,
        UPIHandle.is_active == True
    ).all()

    return {
        "status": "success",
        "data": [
            {
                "upi_id": upi.upi_id,
                "is_primary": upi.is_primary,
                "card_id": str(upi.card_id) if upi.card_id else None
            }
            for upi in upis
        ]
    }


@router.get("/{user_id}")
def get_account_details(
    user_id: str,
    db: Session = Depends(get_db)
):
    account = db.query(Account).filter(
        Account.user_id == user_id
    ).first()

    if not account:
        raise HTTPException(
            status_code=404,
            detail="Account not found"
        )

    return {
        "status": "success",
        "data": {
            "user_id": str(account.user_id),
            "balance": str(account.balance),
            "currency": account.currency,
            "status": account.status,
            "created_at": account.created_at,
            "updated_at": account.updated_at
        },
        "error": None
    }

@router.get("/{user_id}/balance")
def get_balance(user_id: str, db: Session = Depends(get_db)):

    account = get_account_by_user_id(db, user_id)

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    return {
        "user_id": user_id,
        "balance": str(account.balance),
        "currency": account.currency
    }

@router.patch("/{user_id}/freeze")
def freeze_account(user_id: str, db: Session = Depends(get_db)):

    account = db.query(Account).filter(
        Account.user_id == user_id
    ).first()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    if account.status == "closed":
        raise HTTPException(status_code=400, detail="Closed account cannot be modified")

    account.status = "frozen"
    db.commit()

    return {
        "status": "success",
        "message": "Account frozen successfully"
    }


@router.patch("/{user_id}/unfreeze")
def unfreeze_account(user_id: str, db: Session = Depends(get_db)):

    account = db.query(Account).filter(
        Account.user_id == user_id
    ).first()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    account.status = "active"
    db.commit()

    return {
        "status": "success",
        "message": "Account unfrozen successfully"
    }

@router.patch("/{user_id}/close")
def close_account(
    user_id: str,
    db: Session = Depends(get_db)
):
    account = db.query(Account).filter(
        Account.user_id == user_id
    ).first()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    if account.status == "closed":
        raise HTTPException(status_code=400, detail="Account already closed")

    if account.status == "frozen":
        raise HTTPException(status_code=400, detail="Unfreeze account before closing")

    account.status = "closed"

    db.commit()

    return {
        "status": "success",
        "message": "Account closed successfully"
    }