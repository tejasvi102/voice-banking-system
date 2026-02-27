from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.migrations.session import get_db
from app.services.account_service import get_account_by_user_id
from app.models.account import Account

router = APIRouter()

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.migrations.session import get_db
from app.models.account import Account
from app.schemas.account import AccountCreateRequest
from uuid import uuid4

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