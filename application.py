from flask import Flask,request,render_template
import numpy as np
import pandas as pd
from openai import OpenAI
import os


application = Flask(__name__)
app = application

api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)

# Replace with your API key

def get_completion(prompt, model="gpt-3.5-turbo"):
    messages = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(model=model,messages=messages,temperature=0)
    return response.choices[0].message.content

@app.route("/")
def home():    
    return render_template("index.html")

@app.route("/get")
def get_bot_response():    
    userText = request.args.get('msg')  
    response = get_completion(userText)  
    #return str(bot.get_response(userText)) 
    return response
        

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug = True)