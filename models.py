from sqlalchemy import Column, Integer, String, Boolean, DateTime
from database import Base
from sqlalchemy.sql import func


# Define ToDo class inheriting from Base
class ToDo(Base):
    __tablename__ = 'todos'
    id = Column(Integer, primary_key=True)
    task = Column(String(50))
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())