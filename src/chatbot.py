# chatbot.py
import os
from openai import OpenAI

class ChatBot:
    def __init__(self):
        # Load the API key from the environment variable
        api_key = os.getenv('OPENAI_API_KEY')
        self.client = OpenAI(api_key=api_key)

    def get_completion(self, prompt, model="gpt-3.5-turbo"):
        messages = [{"role": "user", "content": prompt}]
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0
        )
        return response.choices[0].message.content
