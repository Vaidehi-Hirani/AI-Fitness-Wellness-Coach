import os
from typing import Any, Dict
from datetime import datetime

from flask import Blueprint, jsonify, request
import google.generativeai as genai

from database import _load_json, _save_json, MEALS_FILE, WORKOUT_LOGS_FILE, WELLNESS_FILE
from chat_agent import CommunicationAgent


bp = Blueprint("api", __name__, url_prefix="/api")


def init_gemini() -> None:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set")
    genai.configure(api_key=api_key)


def gemini_generate(prompt: str, system_instruction: str = "") -> str:
    try:
        init_gemini()
        model = genai.GenerativeModel("gemini-2.5-flash-preview-05-20", system_instruction=system_instruction or None)
        resp = model.generate_content(prompt)
        return (resp.text or "").strip()
    except Exception as e:
        return f"[Generation unavailable: {e}]"


@bp.route("/log/meal", methods=["POST"])
def log_meal():
    payload: Dict[str, Any] = request.get_json(force=True, silent=True) or {}
    username = payload.get("username")
    if not username:
        return jsonify({"error": "username required"}), 400

    meals = _load_json(MEALS_FILE)
    if username not in meals:
        meals[username] = []
    
    meal_entry = {
        **payload,
        "timestamp": datetime.now().isoformat()
    }
    meals[username].append(meal_entry)
    _save_json(MEALS_FILE, meals)
    
    # Immediate feedback
    agent = CommunicationAgent(username)
    feedback = agent.handle("Provide brief nutrition feedback based on my latest meal log.")
    return jsonify({"status": "ok", "feedback": feedback})


@bp.route("/log/workout", methods=["POST"])
def log_workout():
    payload: Dict[str, Any] = request.get_json(force=True, silent=True) or {}
    username = payload.get("username")
    if not username:
        return jsonify({"error": "username required"}), 400
    
    workout_logs = _load_json(WORKOUT_LOGS_FILE)
    if username not in workout_logs:
        workout_logs[username] = []
    
    workout_entry = {
        **payload,
        "timestamp": datetime.now().isoformat()
    }
    workout_logs[username].append(workout_entry)
    _save_json(WORKOUT_LOGS_FILE, workout_logs)
    
    agent = CommunicationAgent(username)
    feedback = agent.handle("Give me concise feedback on my most recent workout log and next steps.")
    return jsonify({"status": "ok", "feedback": feedback})


@bp.route("/log/wellness", methods=["POST"])
def log_wellness():
    payload: Dict[str, Any] = request.get_json(force=True, silent=True) or {}
    username = payload.get("username")
    if not username:
        return jsonify({"error": "username required"}), 400
    
    wellness = _load_json(WELLNESS_FILE)
    if username not in wellness:
        wellness[username] = []
    
    wellness_entry = {
        **payload,
        "timestamp": datetime.now().isoformat()
    }
    wellness[username].append(wellness_entry)
    _save_json(WELLNESS_FILE, wellness)
    
    agent = CommunicationAgent(username)
    feedback = agent.handle("Provide a short recovery recommendation based on my latest wellness log.")
    return jsonify({"status": "ok", "feedback": feedback})


