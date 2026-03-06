import os
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

import models, schemas, database, services

# Create db tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="FitBuddy API")

# Ensure directories exist
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(BASE_DIR, "static", "css"), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "static", "js"), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "templates"), exist_ok=True)

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/users", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = models.User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/api/generate_plan/{user_id}", response_model=schemas.Plan)
def generate_plan_endpoint(user_id: int, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    plan_dict = services.generate_workout_plan(user, user.goal, user.intensity, user.age, user.weight)
    
    db_plan = models.Plan(user_id=user.id, content=plan_dict)
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan

@app.post("/api/feedback/{plan_id}", response_model=schemas.Plan)
def submit_feedback(plan_id: int, feedback: schemas.FeedbackCreate, db: Session = Depends(database.get_db)):
    plan = db.query(models.Plan).filter(models.Plan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
        
    db_feedback = models.Feedback(plan_id=plan.id, text=feedback.text)
    db.add(db_feedback)
    
    # Regenerate plan seamlessly
    new_plan_content = services.refine_workout_plan(plan.content, feedback.text)
    plan.content = new_plan_content
    db.commit()
    db.refresh(plan)
    return plan

@app.post("/api/tips/")
def get_tips(request: schemas.GoalRequest):
    tip = services.generate_tips(request.goal)
    return {"tip": tip}
