from annotated_types import Timezone
from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, text
from sqlalchemy.sql.functions import now

from .database import Base

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    published = Column(Boolean, server_default= 'True',nullable=False)
    create_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("NOW()"))
    is_deleted = Column(Boolean, nullable=False, server_default=text("False"))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("NOW()"))