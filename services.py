import google.generativeai as genai
import os
import json
from schemas import UserCreate

# Ensure GEMINI_API_KEY is available in the environment
API_KEY = os.environ.get("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

# Use the latest gemini model
MODEL_NAME = "gemini-2.5-flash"

def get_model():
    return genai.GenerativeModel(MODEL_NAME)

def generate_workout_plan(user: UserCreate, goal: str, intensity: str, age: int, weight: int) -> dict:
    prompt = f"""
    You are an expert fitness coach. Create a highly personalized 7-day workout plan for the following user:
    - Name: {user.name}
    - Age: {age}
    - Weight: {weight} lbs/kg
    - Goal: {goal}
    - Preferred Intensity: {intensity}

    The plan must be a 7-day schedule with distinct, progressive daily routines. Do not generate the exact same workout for every day. For each day, provide:
    - a 'focus' (e.g., "Full Body Strength", "Upper Body Hypertrophy", "Active Recovery", "Cardio")
    - a list of 'exercises' (with sets and reps if applicable)
    
    CRITICAL: Output ONLY valid JSON, exactly matching this structure, with no markdown formatting, no backticks, just the raw JSON:
    {{
        "day_1": {{"focus": "...", "exercises": ["..."]}},
        "day_2": {{"focus": "...", "exercises": ["..."]}},
        "day_3": {{"focus": "...", "exercises": ["..."]}},
        "day_4": {{"focus": "...", "exercises": ["..."]}},
        "day_5": {{"focus": "...", "exercises": ["..."]}},
        "day_6": {{"focus": "...", "exercises": ["..."]}},
        "day_7": {{"focus": "...", "exercises": ["..."]}}
    }}
    """
    try:
        model = get_model()
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
        return json.loads(text.strip())
    except Exception as e:
        print(f"Error generating plan: {e}")
        # Explicit dummy data for fallback
        return {
            "day_1": {"focus": "Full Body Basics", "exercises": ["Squats 3x10", "Pushups 3x10", "Plank 3x30s"]},
            "day_2": {"focus": "Active Recovery", "exercises": ["30 min light walking", "Stretching"]},
            "day_3": {"focus": "Upper Body", "exercises": ["Dumbbell Press 3x10", "Rows 3x10"]},
            "day_4": {"focus": "Lower Body", "exercises": ["Lunges 3x12", "Glute Bridges 3x15"]},
            "day_5": {"focus": "Cardio", "exercises": ["20 min HIIT", "Jump rope"]},
            "day_6": {"focus": "Core & Stability", "exercises": ["Crunches 3x15", "Russian Twists 3x20"]},
            "day_7": {"focus": "Total Rest", "exercises": ["Rest and recover or consult a trainer."]}
        }

def refine_workout_plan(existing_plan: dict, feedback: str) -> dict:
    prompt = f"""
    You are an expert fitness coach revising an existing 7-day workout plan based on user feedback.
    
    Existing Plan:
    {json.dumps(existing_plan, indent=2)}
    
    User Feedback for changes:
    "{feedback}"
    
    Revise the plan to incorporate the user's feedback. Keep the structure identical. Ensure that the new plan still maintains distinct day-by-day differences unless the feedback explicitly asks for a repetitive routine.
    
    CRITICAL: Output ONLY valid JSON, exactly matching this structure, with no markdown formatting, no backticks, just the raw JSON:
    {{
        "day_1": {{"focus": "...", "exercises": ["..."]}},
        "day_2": {{"focus": "...", "exercises": ["..."]}},
        "day_3": {{"focus": "...", "exercises": ["..."]}},
        "day_4": {{"focus": "...", "exercises": ["..."]}},
        "day_5": {{"focus": "...", "exercises": ["..."]}},
        "day_6": {{"focus": "...", "exercises": ["..."]}},
        "day_7": {{"focus": "...", "exercises": ["..."]}}
    }}
    """
    try:
        model = get_model()
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
        return json.loads(text.strip())
    except Exception as e:
        print(f"Error refining plan: {e}")
        return existing_plan

def generate_tips(goal: str) -> str:
    prompt = f"""
    You are an expert fitness and nutrition coach. 
    The user's primary fitness goal is '{goal}'.
    Provide exactly ONE concise, highly actionable and motivating tip (1-2 sentences) about nutrition or recovery that specifically aligns with this goal. 
    Do not add any greetings or extra text.
    """
    try:
        model = get_model()
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error generating tips: {e}")
        return "Stay hydrated, eat a balanced diet, and ensure you get enough sleep for optimal recovery."
