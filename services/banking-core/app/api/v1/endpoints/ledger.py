from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.migrations.session import get_db
from app.models.account import Account
from app.models.ledger_entry import LedgerEntry

router = APIRouter()


@router.get("/{account_id}")
def get_ledger(account_id: str, db: Session = Depends(get_db)):

    account = db.query(Account).filter(
        Account.id == account_id
    ).first()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    entries = db.query(LedgerEntry).filter(
        LedgerEntry.account_id == account_id
    ).order_by(
        LedgerEntry.created_at.desc()
    ).all()

    return {
        "status": "success",
        "data": {
            "account_id": account_id,
            "entries": [
                {
                    "ledger_id": str(entry.id),
                    "transaction_id": str(entry.transaction_id),
                    "entry_type": entry.entry_type,
                    "amount": str(entry.amount),
                    "currency": entry.currency,
                    "created_at": entry.created_at
                }
                for entry in entries
            ]
        },
        "error": None
    }