from sqlalchemy.orm import Session
from app.models.account import Account


def get_account_by_user_id(db: Session, user_id):
    return db.query(Account).filter(Account.user_id == user_id).first()