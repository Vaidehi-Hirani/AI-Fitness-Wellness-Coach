import os
from typing import List

import google.generativeai as genai


def _ensure_gemini():
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)


def _fallback_workout(level: str, goal: str, duration: int, equipment: str) -> str:
    return (
        f"Workout ({duration} minutes) - Level: {level}, Goal: {goal}\n"
        f"Warm-up: 5 min brisk walk or light cycle\n"
        f"Circuit (3 rounds): 10 squats, 10 push-ups (knees if needed), 20s plank\n"
        f"Cool-down: 5 min easy walk + stretch\n"
        f"Equipment: {equipment or 'bodyweight'}"
    )


def generate_workout(level: str, goal: str, duration: int, equipment: str, gender: str = "", age: int = 0, physical_limitations: str = "") -> str:
    try:
        _ensure_gemini()
        model = genai.GenerativeModel("gemini-2.5-flash-preview-05-20", 
            system_instruction="Design safe, effective workouts considering gender, age, and physical limitations. Be professional and safety-focused.")
        
        # Build comprehensive prompt with all user details
        prompt_parts = [
            "Create a safe, personalized workout plan in 6-10 lines.",
            f"Fitness Level: {level}",
            f"Goal: {goal}",
            f"Duration: {duration} minutes",
            f"Equipment: {equipment}"
        ]
        
        if gender:
            prompt_parts.append(f"Gender: {gender}")
        if age:
            prompt_parts.append(f"Age: {age}")
        if physical_limitations:
            prompt_parts.append(f"IMPORTANT - Physical Limitations: {physical_limitations}")
            prompt_parts.append("CRITICAL: Avoid exercises that could worsen these conditions. Suggest safe alternatives.")
        
        prompt_parts.extend([
            "Include: warm-up, main exercises with sets/reps, and cool-down.",
            "Prioritize safety and proper form over intensity."
        ])
        
        prompt = ". ".join(prompt_parts)
        resp = model.generate_content(prompt)
        text = (resp.text or "").strip()
        return text or _fallback_workout(level, goal, duration, equipment)
    except Exception:
        return _fallback_workout(level, goal, duration, equipment)


