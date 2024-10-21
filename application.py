from flask import Flask, request, render_template, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from src.chatbot import ChatBot
from src.database_models import db, User, ChatMessage
import os


application = Flask(__name__)
app = application
app.secret_key = 'your_secret_key'  
# This line ensures the app knows to look in the 'instance' folder for the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'user.db')
# Ensure the instance folder exists if it doesn’t
os.makedirs(app.instance_path, exist_ok=True)
# Disable modification tracking to save resources
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database with the app
db.init_app(app)  

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# Instantiate the ChatBot class
chatbot = ChatBot()

# The initial page 
@app.route("/")
def landing():
    return render_template("landing.html")

# function is essential for maintaining user sessions across requests.
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Route for user registration
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Try another one.')
            return redirect(url_for('register'))

        # Hash password and create a new user
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful. You can log in now.')
        return redirect(url_for('login'))

    return render_template("register.html")

# Route for user login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        # Verify the password
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('topics'))
        else:
            flash('Invalid username or password.')

    return render_template("login.html")

# Route for user logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Route for the topics page (accessible only after login)
@app.route("/dashboard")
@login_required
def topics():
    return render_template("dashboard.html", username=current_user.username)

@app.route("/dashboard/chatbot")
@login_required
def chatbot_home():
    topic = request.args.get('topic')
    chatbot.set_topic(topic)
    session['topic'] = topic
    chat_history = ChatMessage.query.filter_by(user_id=current_user.id, topic=topic).order_by(ChatMessage.timestamp).all()
    new_chat = len(chat_history) == 0
    return render_template("index.html", topic=topic, username=current_user.username, chat_history=chat_history,new_chat=new_chat)


@app.route("/get")
@login_required
def get_bot_response():
    userText = request.args.get('msg')
    topic = session.get('topic')

    # Save the user's message with the topic
    user_message = ChatMessage(user_id=current_user.id, message=userText, sender="user", topic=topic)
    db.session.add(user_message)
    db.session.commit()

    # Get the chatbot's response
    # response = chatbot.handle_chat(current_user.id,userText,topic)
    session_id = f"{current_user.id}_{topic}"
    response = chatbot.run_chain(userText, session_id)

    # Save the chatbot's response with the topic
    bot_message = ChatMessage(user_id=current_user.id, message=response, sender="bot", topic=topic)
    db.session.add(bot_message)
    db.session.commit()

    return response

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)
