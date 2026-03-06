from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.migrations.session import get_db
from app.services.transaction_service import get_user_transactions
from app.models.transaction import Transaction

router = APIRouter()


# ================================
# Get User Transactions
# ================================
@router.get("/user/{user_id}")
def fetch_transactions(
    user_id: str,
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db)
):

    try:
        UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user_id format")

    transactions = get_user_transactions(
        db=db,
        user_id=user_id,
        limit=limit,
        offset=offset
    )

    if transactions is None:
        raise HTTPException(status_code=404, detail="Account not found")

    return {
        "status": "success",
        "data": {
            "count": len(transactions),
            "limit": limit,
            "offset": offset,
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
        },
        "error": None
    }


# ================================
# Get Single Transaction
# ================================
@router.get("/{transaction_id}")
def get_transaction_detail(
    transaction_id: str,
    db: Session = Depends(get_db)
):

    try:
        UUID(transaction_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid transaction_id")

    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id
    ).first()

    if not transaction:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    return {
        "status": "success",
        "data": {
            "transaction_id": str(transaction.id),
            "from_account_id": str(transaction.from_account_id),
            "to_account_id": str(transaction.to_account_id),
            "amount": str(transaction.amount),
            "currency": transaction.currency,
            "status": transaction.status,
            "created_at": transaction.created_at
        },
        "error": None
    }