from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    age = Column(Integer)
    weight = Column(Integer)
    goal = Column(String)  # e.g., "weight loss", "muscle gain"
    intensity = Column(String) # e.g., "high", "medium", "low"

    plans = relationship("Plan", back_populates="user")

class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    content = Column(JSON) # Store 7-day plan structure here
    generated_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="plans")
    feedbacks = relationship("Feedback", back_populates="plan")

class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("plans.id"))
    text = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    plan = relationship("Plan", back_populates="feedbacks")
