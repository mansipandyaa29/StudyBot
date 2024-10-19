from flask import Flask, request, render_template, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from src.chatbot import ChatBot
import os
from datetime import datetime
from flask_migrate import Migrate


application = Flask(__name__)
app = application
app.secret_key = 'your_secret_key'  # Replace with a secure key
# This line ensures the app knows to look in the 'instance' folder for the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'user.db')
# Ensure the instance folder exists if it doesn’t
os.makedirs(app.instance_path, exist_ok=True)
# Disable modification tracking to save resources
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.String(1000), nullable=False)
    sender = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    topic = db.Column(db.String(150), nullable=False)  # New column to store the topic

    user = db.relationship('User', backref='messages')


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
@app.route("/topics")
@login_required
def topics():
    return render_template("dashboard.html", username=current_user.username)

@app.route("/topics/chatbot")
@login_required
def chatbot_home():
    topic = request.args.get('topic')
    chatbot.set_topic(topic)
    session['topic'] = topic
    # Fetch all messages for the current user and the selected topic
    chat_history = ChatMessage.query.filter_by(user_id=current_user.id, topic=topic).order_by(ChatMessage.timestamp).all()

    return render_template("index.html", topic=topic, username=current_user.username, chat_history=chat_history)


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
    response = chatbot.just_chatbot(userText)

    # Save the chatbot's response with the topic
    bot_message = ChatMessage(user_id=current_user.id, message=response, sender="bot", topic=topic)
    db.session.add(bot_message)
    db.session.commit()

    return response

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)
