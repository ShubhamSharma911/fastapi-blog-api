from fastapi import APIRouter, Request, Header, HTTPException, Depends
import hmac
import hashlib
from app.config import settings
from app import models
from sqlalchemy.orm import Session
from app.database import get_db

router = APIRouter()

@router.post("/webhook/razorpay")
async def razorpay_webhook(
    request: Request,
    db: Session = Depends(get_db),
    x_razorpay_signature: str = Header(None)
):
    body = await request.body()
    secret = settings.razorpay_webhook_secret.encode()


    generated_signature = hmac.new(secret, body, hashlib.sha256).hexdigest()

    if not hmac.compare_digest(generated_signature, x_razorpay_signature):
        raise HTTPException(status_code=400, detail="Invalid signature")

    payload = await request.json()

    # Example processing logic
    razorpay_order_id = payload.get("payload", {}).get("payment", {}).get("entity", {}).get("order_id")
    payment_id = payload.get("payload", {}).get("payment", {}).get("entity", {}).get("id")
    status_ = payload.get("event")

    if razorpay_order_id:
        payment_record = db.query(models.Payment).filter(models.Payment.razorpay_order_id == razorpay_order_id).first()
        if payment_record:
            payment_record.status = status_  # or "paid" or "captured"
            db.commit()
            return {"status": "Webhook processed"}

    raise HTTPException(status_code=404, detail="Payment not found") 