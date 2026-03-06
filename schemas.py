from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

class UserBase(BaseModel):
    name: str
    age: int
    weight: int
    goal: str
    intensity: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int

    class Config:
        from_attributes = True

class PlanBase(BaseModel):
    user_id: int
    content: Dict[str, Any]

class PlanCreate(PlanBase):
    pass

class Plan(PlanBase):
    id: int
    generated_at: datetime

    class Config:
        from_attributes = True

class FeedbackBase(BaseModel):
    plan_id: int
    text: str

class FeedbackCreate(FeedbackBase):
    pass

class Feedback(FeedbackBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class GoalRequest(BaseModel):
    goal: str
