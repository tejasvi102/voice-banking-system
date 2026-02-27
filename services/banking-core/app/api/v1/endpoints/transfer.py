from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.migrations.session import get_db
from app.schemas.transfer import TransferRequest
from app.schemas.transfer_validation import TransferValidationRequest
from app.services.transfer_service import execute_transfer, validate_transfer
from app.core.exceptions import (
    AccountNotFound,
    InsufficientBalance,
    DuplicateTransfer,
    AccountFrozen
)

router = APIRouter()


# ===============================
# Execute Transfer
# ===============================
@router.post("/execute")
def execute_transfer_endpoint(
    request: TransferRequest,
    db: Session = Depends(get_db)
):
    try:
        transaction = execute_transfer(
            db=db,
            from_user_id=request.from_user_id,
            to_user_id=request.to_user_id,
            amount=request.amount,
            currency=request.currency,
            idempotency_key=request.idempotency_key
        )

        return {
            "status": "success",
            "data": {
                "transaction_id": str(transaction.id),
                "amount": str(transaction.amount),
                "currency": transaction.currency
            },
            "error": None
        }

        if amount <= 0:
            raise ValueError("Amount must be greater than zero")

        if from_user_id == to_user_id:
            raise ValueError("Cannot transfer to same account")

        if sender.currency != receiver.currency:
            raise ValueError("Currency mismatch")

    except AccountNotFound:
        raise HTTPException(status_code=404, detail="Account not found")

    except InsufficientBalance:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    except DuplicateTransfer:
        raise HTTPException(status_code=409, detail="Duplicate transfer request")

    except AccountFrozen:
        raise HTTPException(status_code=403, detail="Account is frozen")


# ===============================
# Validate Transfer
# ===============================
@router.post("/validate")
def validate_transfer_endpoint(
    request: TransferValidationRequest,
    db: Session = Depends(get_db)
):
    try:
        allowed, reason = validate_transfer(
            db=db,
            from_user_id=request.from_user_id,
            to_user_id=request.to_user_id,
            amount=request.amount,
            currency=request.currency
        )

        return {
            "status": "success",
            "data": {
                "allowed": allowed,
                "reason": reason
            },
            "error": None
        }

    except AccountNotFound:
        return {
            "status": "error",
            "data": None,
            "error": "Account not found"
        }

    except InsufficientBalance:
        return {
            "status": "error",
            "data": None,
            "error": "Insufficient balance"
        }

    except AccountFrozen:
        return {
            "status": "error",
            "data": None,
            "error": "Account is frozen"
        }