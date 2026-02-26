import os
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.account import Account
from app.models.transaction import Transaction
from decimal import Decimal
from app.core.exceptions import (
    AccountNotFound,
    InsufficientBalance,
    DuplicateTransfer
)


AUTO_CREATE_ACCOUNTS = os.getenv("AUTO_CREATE_ACCOUNTS", "true").lower() == "true"
DEFAULT_INITIAL_BALANCE = Decimal(os.getenv("DEFAULT_INITIAL_BALANCE", "10000"))


def _get_or_create_account(
    db: Session,
    user_id,
    currency: str
):
    account = db.query(Account).filter(
        Account.user_id == user_id
    ).with_for_update().first()

    if account:
        return account

    if not AUTO_CREATE_ACCOUNTS:
        return None

    account = Account(
        user_id=user_id,
        balance=DEFAULT_INITIAL_BALANCE,
        currency=currency
    )
    db.add(account)
    db.flush()
    return account


def execute_transfer(
    db: Session,
    from_user_id,
    to_user_id,
    amount: Decimal,
    currency: str,
    idempotency_key: str
):

    # Idempotency check
    existing = db.query(Transaction).filter(
        Transaction.idempotency_key == idempotency_key
    ).first()

    if existing:
        return existing

    sender = _get_or_create_account(
        db=db,
        user_id=from_user_id,
        currency=currency
    )
    receiver = _get_or_create_account(
        db=db,
        user_id=to_user_id,
        currency=currency
    )


    if not sender or not receiver:
        raise AccountNotFound()

    if sender.balance < amount:
        raise InsufficientBalance()

    if existing:
        raise DuplicateTransfer()

    # Create transaction record
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

def validate_transfer(db, from_user_id, to_user_id, amount, currency):

    sender = db.query(Account).filter(
        Account.user_id == from_user_id
    ).first()

    receiver = db.query(Account).filter(
        Account.user_id == to_user_id
    ).first()

    if not sender or not receiver:
        raise AccountNotFound()

    if sender.currency != currency:
        return False, "Currency mismatch"

    if sender.balance < amount:
        raise InsufficientBalance()

    return True, None