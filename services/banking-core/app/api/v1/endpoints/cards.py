from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.migrations.session import get_db
from app.models.cards import Card
from app.models.account import Account
from app.schemas.card import CardCreateRequest
from app.core.exceptions import AccountNotFound


router = APIRouter()

@router.post("/{user_id}/add-card")
def add_card(user_id: str, request: CardCreateRequest, db: Session = Depends(get_db)):
    
    account = db.query(Account).filter(
        Account.user_id == user_id
    ).first()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    card = Card(
        account_id=account.id,
        card_type=request.card_type,
        card_network=request.card_network,
        last4=request.last4,
        expiry_month=request.expiry_month,
        expiry_year=request.expiry_year
    )

    db.add(card)
    db.commit()

    return {
        "status": "success",
        "message": "Card added successfully"
    }

@router.get("/{user_id}/cards")
def get_cards(user_id: str, db: Session = Depends(get_db)):

    account = db.query(Account).filter(
        Account.user_id == user_id
    ).first()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    cards = db.query(Card).filter(
        Card.account_id == account.id
    ).all()

    return {
        "status": "success",
        "data": [
            {
                "card_id": str(card.id),
                "card_type": card.card_type,
                "network": card.card_network,
                "last4": card.last4,
                "expiry_month": card.expiry_month,
                "expiry_year": card.expiry_year,
                "is_active": card.is_active
            }
            for card in cards
        ]
    }

@router.get("/{account_id}")
def get_cards(account_id: str, db: Session = Depends(get_db)):

    account = db.query(Account).filter(
        Account.id == account_id
    ).first()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    cards = db.query(Card).filter(
        Card.account_id == account_id,
        Card.is_active == True
    ).all()

    return {
        "status": "success",
        "data": {
            "account_id": account_id,
            "cards": [
                {
                    "card_id": str(card.id),
                    "card_type": card.card_type,
                    "card_network": card.card_network,
                    "last4": card.last4,
                    "expiry_month": card.expiry_month,
                    "expiry_year": card.expiry_year,
                    "is_active": card.is_active,
                    "created_at": card.created_at
                }
                for card in cards
            ]
        },
        "error": None
    }

@router.patch("/{card_id}/deactivate")
def deactivate_card(card_id: str, db: Session = Depends(get_db)):

    card = db.query(Card).filter(Card.id == card_id).first()

    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    card.is_active = False
    db.commit()

    return {
        "status": "success",
        "message": "Card deactivated"
    }