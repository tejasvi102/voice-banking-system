import os
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime

from app.models.account import Account
from app.models.transaction import Transaction
from app.models.upi_handle import UPIHandle
from app.models.ledger_entry import LedgerEntry

from app.core.exceptions import (
    AccountNotFound,
    InsufficientBalance,
    DuplicateTransfer,
    AccountFrozen
)

DAILY_TRANSFER_LIMIT = Decimal(os.getenv("DAILY_TRANSFER_LIMIT", "100000"))


# ==================================================
# Execute Transfer (UPI Based)
# ==================================================
def execute_transfer(
    db: Session,
    from_user_id,
    to_upi_id: str,
    amount: Decimal,
    currency: str,
    idempotency_key: str
):

    # -----------------------
    # Idempotency check
    # -----------------------
    existing = db.query(Transaction).filter(
        Transaction.idempotency_key == idempotency_key
    ).first()

    if existing:
        return existing

    # -----------------------
    # Fetch sender
    # -----------------------
    sender = db.query(Account).filter(
        Account.user_id == from_user_id
    ).with_for_update().first()

    if not sender:
        raise AccountNotFound()

    # -----------------------
    # Resolve UPI
    # -----------------------
    upi = db.query(UPIHandle).filter(
        UPIHandle.upi_id == to_upi_id,
        UPIHandle.is_active == True
    ).first()

    if not upi:
        raise ValueError("Invalid UPI ID")

    # -----------------------
    # Fetch receiver
    # -----------------------
    receiver = db.query(Account).filter(
        Account.id == upi.account_id
    ).with_for_update().first()

    if not receiver:
        raise AccountNotFound()

    # -----------------------
    # Validations
    # -----------------------
    if amount <= 0:
        raise ValueError("Amount must be greater than zero")

    if sender.id == receiver.id:
        raise ValueError("Cannot transfer to self")

    if sender.status != "active":
        raise AccountFrozen()

    if receiver.status != "active":
        raise AccountFrozen()

    if sender.currency != currency:
        raise ValueError("Currency mismatch")

    if sender.balance < amount:
        raise InsufficientBalance()

    # -----------------------
    # Create Transaction
    # -----------------------
    transaction = Transaction(
        from_account_id=sender.id,
        to_account_id=receiver.id,
        amount=amount,
        currency=currency,
        status="pending",
        idempotency_key=idempotency_key
    )

    db.add(transaction)
    db.flush()

    # -----------------------
    # Update balances
    # -----------------------
    sender.balance -= amount
    receiver.balance += amount

    transaction.status = "success"

    # -----------------------
    # Ledger entries (double entry)
    # -----------------------
    debit_entry = LedgerEntry(
        account_id=sender.id,
        transaction_id=transaction.id,
        entry_type="debit",
        amount=amount,
        currency=currency
    )

    credit_entry = LedgerEntry(
        account_id=receiver.id,
        transaction_id=transaction.id,
        entry_type="credit",
        amount=amount,
        currency=currency
    )

    db.add(debit_entry)
    db.add(credit_entry)

    db.commit()
    db.refresh(transaction)

    return transaction


# ==================================================
# Validate Transfer (UPI Based)
# ==================================================
def validate_transfer(
    db: Session,
    from_user_id,
    to_upi_id: str,
    amount: Decimal,
    currency: str
):

    sender = db.query(Account).filter(
        Account.user_id == from_user_id
    ).first()

    if not sender:
        raise AccountNotFound()

    # Resolve UPI
    upi = db.query(UPIHandle).filter(
        UPIHandle.upi_id == to_upi_id,
        UPIHandle.is_active == True
    ).first()

    if not upi:
        return False, "Invalid UPI ID"

    receiver = db.query(Account).filter(
        Account.id == upi.account_id
    ).first()

    if not receiver:
        return False, "Invalid UPI ID"

    # -----------------------
    # Validations
    # -----------------------
    if amount <= 0:
        return False, "Amount must be greater than zero"

    if sender.id == receiver.id:
        return False, "Cannot transfer to self"

    if sender.status != "active":
        return False, "Sender account frozen"

    if receiver.status != "active":
        return False, "Receiver account frozen"

    if sender.currency != currency:
        return False, "Currency mismatch"

    if sender.balance < amount:
        return False, "Insufficient balance"

    # -----------------------
    # Daily Limit Check
    # -----------------------
    today = datetime.utcnow().date()

    total_today = db.query(
        func.coalesce(func.sum(Transaction.amount), 0)
    ).filter(
        Transaction.from_account_id == sender.id,
        Transaction.status == "success",
        func.date(Transaction.created_at) == today
    ).scalar()

    if Decimal(total_today) + amount > DAILY_TRANSFER_LIMIT:
        return False, "Daily transfer limit exceeded"

    return True, None