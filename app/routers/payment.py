from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import schemas
from app.services import payment_services
from app.database import get_db

router = APIRouter(prefix="/payment", tags=["Payment"])

@router.post("/create-order", response_model=schemas.CreateOrderResponse)
def create_order(payload: schemas.CreateOrderRequest, db: Session = Depends(get_db)):
    try:
        razorpay_order = payment_services.create_payment_order(payload, db)
        return schemas.CreateOrderResponse(
            order_id=razorpay_order["id"],
            amount=razorpay_order["amount"],
            currency=razorpay_order["currency"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )