import os
import json
from typing import Optional, Dict, Any, List
from datetime import datetime

# JSON file-based storage for moderate-term memory
DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")
WORKOUTS_FILE = os.path.join(DATA_DIR, "workouts.json")
CHAT_FILE = os.path.join(DATA_DIR, "chat.json")
MEALS_FILE = os.path.join(DATA_DIR, "meals.json")
WORKOUT_LOGS_FILE = os.path.join(DATA_DIR, "workout_logs.json")
WELLNESS_FILE = os.path.join(DATA_DIR, "wellness.json")

def _ensure_data_dir():
    """Create data directory if it doesn't exist."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def _load_json(file_path: str, default: Any = None) -> Any:
    """Load data from JSON file."""
    _ensure_data_dir()
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return default or {}
    return default or {}

def _save_json(file_path: str, data: Any) -> None:
    """Save data to JSON file."""
    _ensure_data_dir()
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def init_db() -> None:
    """Initialize database - using JSON file storage for moderate-term memory."""
    print("Using JSON file storage for moderate-term memory")
    _ensure_data_dir()


def add_user(name: str, age: int, gender: str, fitness_level: str, goal: str, equipment: str, physical_limitations: str = "") -> bool:
    """Create or update a user profile."""
    users = _load_json(USERS_FILE)
    users[name] = {
        "name": name,
        "age": age,
        "gender": gender,
        "fitness_level": fitness_level,
        "goal": goal,
        "equipment": equipment,
        "physical_limitations": physical_limitations,
        "created_at": datetime.now().isoformat(),
        "last_updated": datetime.now().isoformat()
    }
    _save_json(USERS_FILE, users)
    return True


class User:
    def __init__(self, data: Dict[str, Any]):
        self.name: str = data.get("name", "")
        self.age: Optional[int] = data.get("age")
        self.gender: str = data.get("gender", "")
        self.fitness_level: str = data.get("fitness_level", "")
        self.goal: str = data.get("goal", "")
        self.equipment: str = data.get("equipment", "")
        self.physical_limitations: str = data.get("physical_limitations", "")


def get_user(username: str) -> Optional[User]:
    users = _load_json(USERS_FILE)
    if username in users:
        return User(users[username])
    return None


def save_workout(username: str, workout_text: str) -> None:
    workouts = _load_json(WORKOUTS_FILE)
    workouts[username] = {
        "text": workout_text,
        "timestamp": datetime.now().isoformat()
    }
    _save_json(WORKOUTS_FILE, workouts)


def get_last_workout(username: str) -> Optional[str]:
    workouts = _load_json(WORKOUTS_FILE)
    if username in workouts:
        return workouts[username].get("text")
    return None


def save_chat_message(username: str, role: str, message: str) -> None:
    chat_data = _load_json(CHAT_FILE)
    if username not in chat_data:
        chat_data[username] = []
    
    chat_data[username].append({
        "role": role,
        "message": message,
        "timestamp": datetime.now().isoformat()
    })
    
    # Keep only last 50 messages per user to prevent file from growing too large
    if len(chat_data[username]) > 50:
        chat_data[username] = chat_data[username][-50:]
    
    _save_json(CHAT_FILE, chat_data)


def get_recent_wellness_logs(username: str, limit: int = 3) -> List[Dict[str, Any]]:
    wellness_data = _load_json(WELLNESS_FILE)
    if username in wellness_data:
        # Sort by timestamp and return most recent
        user_logs = wellness_data[username]
        sorted_logs = sorted(user_logs, key=lambda x: x.get('timestamp', ''), reverse=True)
        return sorted_logs[:limit]
    return []


def get_user_chat_history(username: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Get recent chat history for a user."""
    chat_data = _load_json(CHAT_FILE)
    if username in chat_data:
        return chat_data[username][-limit:]
    return []


def get_user_stats(username: str) -> Dict[str, Any]:
    """Get comprehensive user statistics."""
    users = _load_json(USERS_FILE)
    meals = _load_json(MEALS_FILE)
    workout_logs = _load_json(WORKOUT_LOGS_FILE)
    wellness = _load_json(WELLNESS_FILE)
    chat_data = _load_json(CHAT_FILE)
    
    return {
        "profile": users.get(username, {}),
        "total_meals": len(meals.get(username, [])),
        "total_workouts": len(workout_logs.get(username, [])),
        "total_wellness_logs": len(wellness.get(username, [])),
        "total_chat_messages": len(chat_data.get(username, [])),
        "last_activity": max([
            users.get(username, {}).get("last_updated", ""),
            meals.get(username, [{}])[-1].get("timestamp", "") if meals.get(username) else "",
            workout_logs.get(username, [{}])[-1].get("timestamp", "") if workout_logs.get(username) else "",
            wellness.get(username, [{}])[-1].get("timestamp", "") if wellness.get(username) else "",
        ])
    }

