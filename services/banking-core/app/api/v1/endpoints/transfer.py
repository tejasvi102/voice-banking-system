from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.migrations.session import get_db
from app.schemas.transfer import TransferRequest
from app.services.transfer_service import execute_transfer
from app.core.exceptions import (
    AccountNotFound,
    InsufficientBalance,
    DuplicateTransfer
)
from app.api.v1.endpoints import accounts, transactions

from app.schemas.transfer_validation import TransferValidationRequest
from app.services.transfer_service import validate_transfer
from app.core.exceptions import AccountNotFound, InsufficientBalance
router = APIRouter()


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
            "transaction_id": str(transaction.id),
            "amount": str(transaction.amount),
            "currency": transaction.currency
        }

    except AccountNotFound:
        raise HTTPException(status_code=404, detail="Account not found")

    except InsufficientBalance:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    except DuplicateTransfer:
        raise HTTPException(status_code=409, detail="Duplicate transfer request")

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
            "allowed": allowed,
            "reason": reason
        }

    except AccountNotFound:
        return {
            "allowed": False,
            "reason": "Account not found"
        }

    except InsufficientBalance:
        return {
            "allowed": False,
            "reason": "Insufficient balance"
        }