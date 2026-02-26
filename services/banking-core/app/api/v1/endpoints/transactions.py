from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.migrations.session import get_db
from app.services.transaction_service import get_user_transactions

router = APIRouter()


@router.get("/{user_id}")
def fetch_transactions(user_id: str, db: Session = Depends(get_db)):

    transactions = get_user_transactions(db, user_id)

    if transactions is None:
        raise HTTPException(status_code=404, detail="Account not found")

    return {
        "count": len(transactions),
        "transactions": [
            {
                "transaction_id": str(tx.id),
                "from_account_id": str(tx.from_account_id),
                "to_account_id": str(tx.to_account_id),
                "amount": str(tx.amount),
                "currency": tx.currency,
                "status": tx.status,
                "created_at": tx.created_at
            }
            for tx in transactions
        ]
    }