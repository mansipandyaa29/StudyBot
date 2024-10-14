from flask import Flask,request,render_template
import numpy as np
import pandas as pd
from openai import OpenAI
import os

from src.chatbot import ChatBot

application = Flask(__name__)
app = application

# Instantiate the ChatBot class
chatbot = ChatBot()

# Route for the landing page
@app.route("/")
def landing():    
    return render_template("landing.html")

# Route for the chatbot page
@app.route("/topics")
def topics():    
    return render_template("topics.html")

# Route for the chatbot page
@app.route("/chatbot")
def chatbot():    
    return render_template("index.html")

@app.route("/get")
def get_bot_response():    
    userText = request.args.get('msg')  
    response = chatbot.get_completion(userText) 
    return response

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug = True)