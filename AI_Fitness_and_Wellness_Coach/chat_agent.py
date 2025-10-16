from typing import Dict, Any, Optional
import os

import google.generativeai as genai

from database import save_chat_message, get_recent_wellness_logs, get_user_chat_history, get_user_stats


def _ensure_gemini():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set")
    genai.configure(api_key=api_key)


class DataAnalystAgent:
    def __init__(self, username: str):
        self.username = username

    def get_standardized_metrics(self) -> Dict[str, Any]:
        # Get comprehensive user stats from JSON storage
        stats = get_user_stats(self.username)
        return {
            "num_meals": stats.get("total_meals", 0),
            "num_workout_logs": stats.get("total_workouts", 0),
            "num_wellness_logs": stats.get("total_wellness_logs", 0),
            "profile": stats.get("profile", {}),
            "last_activity": stats.get("last_activity", ""),
            "total_chat_messages": stats.get("total_chat_messages", 0)
        }


class FitnessPlanningAgent:
    def plan(self, context: Dict[str, Any], user_message: str) -> str:
        _ensure_gemini()
        model = genai.GenerativeModel("gemini-2.5-flash-preview-05-20", 
            system_instruction="You are a professional fitness coach. Consider gender, age, and physical limitations when giving advice. Be smart about response length: give detailed plans for complex requests but keep simple questions brief. Always prioritize safety and proper form.")
        
        profile = context.get('profile', {})
        prompt_parts = [
            f"User Query: {user_message}",
            f"User Profile: {profile}",
            "Analyze the request and provide an appropriate response."
        ]
        
        # Add safety considerations if physical limitations exist
        if profile.get('physical_limitations'):
            prompt_parts.append(f"IMPORTANT: User has physical limitations: {profile.get('physical_limitations')}. Avoid exercises that could worsen these conditions and suggest safe alternatives.")
        
        # Add gender and age considerations
        if profile.get('gender'):
            prompt_parts.append(f"Consider gender-specific recommendations for: {profile.get('gender')}")
        if profile.get('age'):
            prompt_parts.append(f"Consider age-appropriate exercises for: {profile.get('age')} years old")
        
        prompt = "\n".join(prompt_parts)
        try:
            resp = model.generate_content(prompt)
            return (resp.text or "").strip()
        except Exception as e:
            return f"Training guidance unavailable: {e}"


class NutritionPlanningAgent:
    def plan(self, context: Dict[str, Any], user_message: str) -> str:
        _ensure_gemini()
        model = genai.GenerativeModel("gemini-2.5-flash-preview-05-20", 
            system_instruction="You are a practical dietitian. Be intelligent about response length: give detailed meal plans, recipes, and nutrition programs when requested, but keep simple questions brief. Always provide actionable advice.")
        prompt = f"User: {user_message}\nContext: {context.get('profile', {})}\nAnalyze the request and provide an appropriate response - detailed for meal plans/programs, brief for simple questions."
        try:
            resp = model.generate_content(prompt)
            return (resp.text or "").strip()
        except Exception as e:
            return f"Nutrition guidance unavailable: {e}"


class WellnessRecoveryAgent:
    def plan(self, context: Dict[str, Any], user_message: str) -> str:
        _ensure_gemini()
        model = genai.GenerativeModel("gemini-2.5-flash-preview-05-20", 
            system_instruction="You are a supportive wellness coach. Be smart about response length: give detailed recovery plans and protocols when needed, but keep simple questions brief. Always provide practical, empathetic advice.")
        prompt = f"User: {user_message}\nContext: {context.get('profile', {})}\nAnalyze the request and provide an appropriate response - detailed for recovery plans, brief for simple questions."
        try:
            resp = model.generate_content(prompt)
            return (resp.text or "").strip()
        except Exception as e:
            return f"Recovery guidance unavailable: {e}"


class CommunicationAgent:
    def __init__(self, username: str):
        self.username = username
        self.analyst = DataAnalystAgent(username)
        self.fitness = FitnessPlanningAgent()
        self.nutrition = NutritionPlanningAgent()
        self.wellness = WellnessRecoveryAgent()

    def route_intent(self, message: str) -> str:
        text = message.lower()
        if any(k in text for k in ["workout", "training", "exercise", "gym"]):
            return "fitness"
        if any(k in text for k in ["calorie", "meal", "protein", "diet", "macro"]):
            return "nutrition"
        if any(k in text for k in ["sleep", "stress", "recovery", "hydrate", "fatigue"]):
            return "wellness"
        return "mixed"

    def synthesize(self, parts: Dict[str, str]) -> str:
        _ensure_gemini()
        model = genai.GenerativeModel("gemini-2.5-flash-preview-05-20", 
            system_instruction="You are an intelligent fitness coach. Analyze the user's request and provide an appropriate response. For simple questions, be brief. For complex requests (meal plans, workout programs), be comprehensive and detailed. Always be practical and helpful.")
        prompt = "\n".join([f"{k.upper()}: {v}" for k, v in parts.items() if v])
        try:
            resp = model.generate_content(f"Based on these agent insights, provide an intelligent response that matches the complexity of the user's request:\n{prompt}")
            return (resp.text or "").strip()
        except Exception:
            # Fallback: simple join
            return " ".join([v for v in parts.values() if v])

    def _should_reduce_intensity(self) -> bool:
        logs = get_recent_wellness_logs(self.username, limit=3)
        poor = 0
        for row in logs:
            # Expect keys like sleep_quality (0-100) or stress_level (1-5)
            sleep_quality = row.get("sleep_quality")
            stress_level = row.get("stress_level")
            if sleep_quality is not None and isinstance(sleep_quality, (int, float)) and sleep_quality < 50:
                poor += 1
            elif stress_level is not None and isinstance(stress_level, (int, float)) and stress_level >= 4:
                poor += 1
        return poor >= 3

    def handle(self, message: str) -> str:
        # Handle simple greetings and common responses quickly
        message_lower = message.lower().strip()
        
        if message_lower in ["hi", "hello", "hey", "hi there"]:
            reply = f"Hi {self.username}! 👋 I'm your AI fitness coach. What can I help you with today?"
        elif message_lower in ["thanks", "thank you", "thx"]:
            reply = "You're welcome! Keep up the great work! 💪"
        elif message_lower in ["bye", "goodbye", "see you"]:
            reply = "See you later! Stay consistent with your fitness goals! 🏃‍♀️"
        else:
            # Use multi-agent system for complex queries
            context = self.analyst.get_standardized_metrics()
            
            # Add chat history context for better memory
            chat_history = get_user_chat_history(self.username, limit=3)
            context["recent_chat"] = chat_history
            
            # Add the original message to context for better analysis
            context["original_message"] = message
            
            intent = self.route_intent(message)

            outputs: Dict[str, str] = {}
            if intent == "fitness":
                if self._should_reduce_intensity():
                    message = message + "\nNOTE: Reduce intensity by ~30% this week due to recovery risk."
                outputs["fitness"] = self.fitness.plan(context, message)
            elif intent == "nutrition":
                outputs["nutrition"] = self.nutrition.plan(context, message)
            elif intent == "wellness":
                outputs["wellness"] = self.wellness.plan(context, message)
            else:
                # Mixed: get inputs from all agents
                mixed_msg = message
                if self._should_reduce_intensity():
                    mixed_msg = mixed_msg + "\nNOTE: Reduce intensity by ~30% this week due to recovery risk."
                outputs["fitness"] = self.fitness.plan(context, mixed_msg)
                outputs["nutrition"] = self.nutrition.plan(context, message)
                outputs["wellness"] = self.wellness.plan(context, message)

            reply = self.synthesize(outputs)
        
        # Persist chat transcript
        try:
            save_chat_message(self.username, "user", message)
            save_chat_message(self.username, "coach", reply)
        except Exception:
            pass
        return reply


def chat_with_ai(user_message: str, username: Optional[str] = "Guest") -> str:
    try:
        agent = CommunicationAgent(username or "Guest")
        return agent.handle(user_message)
    except Exception as e:
        return f"I'm having trouble responding right now: {e}"


