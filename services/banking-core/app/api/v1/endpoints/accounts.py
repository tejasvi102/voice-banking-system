from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.migrations.session import get_db
from app.services.account_service import get_account_by_user_id

router = APIRouter()


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