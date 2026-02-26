import uuid
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.models.account import Account
from app.models.transaction import Transaction


def get_user_transactions(db: Session, user_id: str):
    try:
        user_uuid = uuid.UUID(user_id)
    except (TypeError, ValueError):
        return None

    account = db.query(Account).filter(Account.user_id == user_uuid).first()
    if not account:
        return None

    return (
        db.query(Transaction)
        .filter(
            or_(
                Transaction.from_account_id == account.id,
                Transaction.to_account_id == account.id
            )
        )
        .order_by(Transaction.created_at.desc())
        .all()
    )
