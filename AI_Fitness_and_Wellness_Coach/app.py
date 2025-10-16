import os
from flask import Flask, render_template, request, redirect, url_for, session
from database import init_db, get_user, add_user, save_workout, get_last_workout
from workout_generator import generate_workout
from chat_agent import chat_with_ai
from logger import log_message
from api import bp as api_bp
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask App
app = Flask(__name__)
# Set a secret key for sessions (required for flash messages and sessions)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "a_very_secret_default_key")

# Initialize the database on startup
init_db()
app.register_blueprint(api_bp)

# --- Global State for Chat (Alternative to using Flask Session directly for the chat history) ---
# In a real app, this should be tied to a user session or database
chat_history = [] 

# --- Routes ---

@app.route('/')
def home():
    """Home page."""
    log_message("Home page accessed.", "info")
    return render_template('home.html', title='Home')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page and handler."""
    if request.method == 'POST':
        try:
            name = request.form['name']
            age = int(request.form['age'])
            gender = request.form['gender']
            level = request.form['fitness_level']
            goal = request.form['goal']
            equipment = request.form['equipment']
            physical_limitations = request.form.get('physical_limitations', '')

            if add_user(name, age, gender, level, goal, equipment, physical_limitations):
                log_message(f"User registered/updated successfully via Flask: {name}", "info")
                session['username'] = name  # Store username in session
                return redirect(url_for('workout'))
            else:
                return render_template('register.html', error="Registration failed. Check logs.")
        except ValueError:
             return render_template('register.html', error="Invalid age value.")
        except Exception as e:
            log_message(f"Registration POST failed: {e}", "error")
            return render_template('register.html', error=f"An unexpected error occurred: {str(e)}")
            
    # GET request
    log_message("Registration page accessed.", "info")
    return render_template('register.html', title='Register')

@app.route('/workout', methods=['GET', 'POST'])
def workout():
    """Workout generation page."""
    username = session.get('username')
    if not username:
        return redirect(url_for('register'))
    
    user = get_user(username)
    if not user:
        return redirect(url_for('register'))

    if request.method == 'POST':
        # The user clicks "Generate Workout"
        try:
            log_message(f"Attempting to generate workout for {username}.", "info")
            
            # The duration is hardcoded to 30 mins as a default for this demo structure
            workout_plan = generate_workout(
                user.fitness_level, 
                user.goal, 
                30, 
                user.equipment,
                user.gender,
                user.age,
                user.physical_limitations
            )

            # Check for error message from the generator
            if workout_plan.startswith("Error occurred"):
                return render_template('workout.html', user=user, error=workout_plan)

            save_workout(username, workout_plan)
            session['last_plan'] = workout_plan # Store temporarily for result page
            return redirect(url_for('result'))
        
        except Exception as e:
            log_message(f"Workout generation failed for {username}: {e}", "error")
            return render_template('workout.html', user=user, error=f"Failed to generate workout: {str(e)}")

    # GET request
    log_message(f"Workout page accessed for {username}.", "info")
    last_plan = get_last_workout(username)
    return render_template('workout.html', user=user, last_plan=last_plan, title='Generate Workout')

@app.route('/result')
def result():
    """Displays the generated workout plan."""
    username = session.get('username')
    if not username:
        return redirect(url_for('register'))
    
    workout_plan = get_last_workout(username)
    
    if not workout_plan:
        return redirect(url_for('workout'))

    log_message(f"Result page accessed for {username}.", "info")
    return render_template('result.html', title='Workout Plan', username=username, plan=workout_plan)

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    """AI Chat Agent interaction page."""
    username = session.get('username', 'Guest')
    
    if request.method == 'POST':
        user_message = request.form['message']
        if user_message:
            log_message(f"Chat received from {username}: {user_message}", "info")
            # Get response from the AI
            ai_response = chat_with_ai(user_message, username)
            log_message(f"AI response sent to {username}", "info")

    # Load chat history from JSON storage
    from database import get_user_chat_history
    chat_history = get_user_chat_history(username, limit=50)  # Get last 50 messages
    
    log_message(f"Chat page accessed by {username}.", "info")
    return render_template('chat.html', title='AI Coach Chat', history=chat_history, username=username)


if __name__ == '__main__':
    # Flask runs on port 5000 by default
    app.run(debug=True, port=5000)
