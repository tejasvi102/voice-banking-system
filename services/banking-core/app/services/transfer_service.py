import os
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime

from app.models.account import Account
from app.models.transaction import Transaction
from app.core.exceptions import (
    AccountNotFound,
    InsufficientBalance,
    DuplicateTransfer,
    AccountFrozen
)

AUTO_CREATE_ACCOUNTS = os.getenv("AUTO_CREATE_ACCOUNTS", "false").lower() == "false"
DEFAULT_INITIAL_BALANCE = Decimal(os.getenv("DEFAULT_INITIAL_BALANCE", "10000"))

DAILY_TRANSFER_LIMIT = Decimal(os.getenv("DAILY_TRANSFER_LIMIT", "100000"))


# ==================================================
# Account Helper
# ==================================================
def _get_or_create_account(db: Session, user_id, currency: str):

    account = (
        db.query(Account)
        .filter(Account.user_id == user_id)
        .with_for_update()
        .first()
    )

    if account:
        return account

    if not AUTO_CREATE_ACCOUNTS:
        return None

    account = Account(
        user_id=user_id,
        balance=DEFAULT_INITIAL_BALANCE,
        currency=currency,
        status="active"
    )

    db.add(account)
    db.flush()

    return account


# ==================================================
# Execute Transfer (Atomic + Safe)
# ==================================================
def execute_transfer(
    db: Session,
    from_user_id,
    to_user_id,
    amount: Decimal,
    currency: str,
    idempotency_key: str
):

    # Idempotency check
    existing = (
        db.query(Transaction)
        .filter(Transaction.idempotency_key == idempotency_key)
        .first()
    )

    if existing:
        return existing

    sender = _get_or_create_account(db, from_user_id, currency)
    receiver = _get_or_create_account(db, to_user_id, currency)

    if not sender or not receiver:
        raise AccountNotFound()

    if sender.status != "active":
        raise Exception("Sender account is not active")

    if receiver.status != "active":
        raise Exception("Receiver account is not active")

    if sender.currency != currency:
        raise ValueError("Currency mismatch")

    if sender.balance < amount:
        raise InsufficientBalance()

    # Create transaction
    transaction = Transaction(
        from_account_id=sender.id,
        to_account_id=receiver.id,
        amount=amount,
        currency=currency,
        status="pending",
        idempotency_key=idempotency_key
    )

    db.add(transaction)

    # Update balances
    sender.balance -= amount
    receiver.balance += amount

    transaction.status = "success"

    db.commit()
    db.refresh(transaction)

    return transaction

# ==================================================
# Validate Transfer (No Money Movement)
# ==================================================
def validate_transfer(db, from_user_id, to_user_id, amount, currency):

    sender = db.query(Account).filter(
        Account.user_id == from_user_id
    ).first()

    receiver = db.query(Account).filter(
        Account.user_id == to_user_id
    ).first()

    if not sender or not receiver:
        raise AccountNotFound()

    if sender.status != "active":
        raise AccountFrozen()

    if receiver.status != "active":
        raise AccountFrozen()

    if sender.currency != currency:
        return False, "Currency mismatch"

    if sender.balance < amount:
        raise InsufficientBalance()

    # Daily limit check
    today = datetime.utcnow().date()

    total_today = (
        db.query(func.coalesce(func.sum(Transaction.amount), 0))
        .filter(
            Transaction.from_account_id == sender.id,
            Transaction.status == "success",
            func.date(Transaction.created_at) == today
        )
        .scalar()
    )

    if Decimal(total_today) + amount > DAILY_TRANSFER_LIMIT:
        return False, "Daily transfer limit exceeded"

    return True, None