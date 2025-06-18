from sqlalchemy.orm import Session
from app import models, schemas
import razorpay
from app.config import settings

client = razorpay.Client(auth=(settings.razorpay_key_id, settings.razorpay_key_secret))

def create_payment_order(payload: schemas.CreateOrderRequest, db: Session):
    # Razorpay expects amount in paise
    amount_paise = int(payload.amount * 100)

    order_data = {
        "amount": amount_paise,
        "currency": "INR",
        "payment_capture": 1
    }

    razorpay_order = client.order.create(data=order_data)

    # Save in DB
    new_payment = models.Payment(
        user_id=payload.user_id,
        razorpay_order_id=razorpay_order["id"],
        amount=payload.amount,
        status="created"
    )
    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)

    return razorpay_order