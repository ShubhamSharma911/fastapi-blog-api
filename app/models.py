from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, text, ForeignKey, DateTime, UniqueConstraint, func, \
    Enum as SqlEnum, Float
from sqlalchemy.orm import relationship
from app.role import Role

from app.database import Base
from app.status import Status

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    published = Column(Boolean, server_default= 'True',nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("NOW()"))
    is_deleted = Column(Boolean, nullable=False, server_default=text("False"))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("NOW()"))
    owner_id = Column(Integer, ForeignKey("users.id", ondelete = 'CASCADE'), nullable=False)
    owner = relationship("User")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, nullable = False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    is_deleted = Column(Boolean, nullable=False, server_default=text("False"))
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("NOW()"))
    is_active = Column(Boolean, nullable=False, server_default=text("True"))

    role_id = Column(Integer, ForeignKey("roles.id"))
    role = relationship("Role")


class Vote(Base):
    __tablename__ = "votes"
    user_id = Column(Integer, ForeignKey("users.id", ondelete='CASCADE'), primary_key=True, nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete='CASCADE'), primary_key=True, nullable=False)



class Resume(Base):
    __tablename__ = "resumes"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    filename = Column(String, nullable=False)
    filepath = Column(String, nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(SqlEnum(Status), nullable=False, server_default=Status.NOT_STARTED.value)

    __table_args__ = (UniqueConstraint('user_id', name='uq_user_resume'),)

class PDF(Base):
    __tablename__ = "pdfs"
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("NOW()"))
    filename = Column(String, nullable=False)
    filepath = Column(String, nullable=False)
    is_deleted = Column(Boolean, nullable=False, server_default=text("False"))


#-------------------PAYMENT-------------
class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    razorpay_order_id = Column(String, unique=True, nullable=False)
    razorpay_payment_id = Column(String, nullable=True)
    razorpay_signature = Column(String, nullable=True)

    amount = Column(Float, nullable=False)
    status = Column(String, default="created")  # 'created', 'paid', 'failed'

    created_at = Column(DateTime(timezone=True), server_default=func.now())