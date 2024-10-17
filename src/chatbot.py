# chatbot.py
import os
from langchain_openai import OpenAI
from langchain.memory import ConversationSummaryBufferMemory
from langchain.chains import ConversationChain



class ChatBot:
    def __init__(self):
        # Load the API key from the environment variable
        api_key = os.getenv('OPENAI_API_KEY')
        self.client = OpenAI(api_key=api_key)
        self.topic = None
        self.memory = ConversationSummaryBufferMemory(llm=self.client, max_token_limit=100)
        self.conversation = ConversationChain(llm=self.client)
    
    def set_topic(self, topic):
        self.topic = topic

    def get_completion(self, prompt, model="gpt-4o"):
        # prompt = f"""
        # You are a my interviewer and its my {self.topic} interview. 
        # Ask me questions and my replies will be the answers I type out. 
        # Tell me how I do and keep asking 10 unique and different questions . 
        # Try to cover all the possible questions.
        # """
        messages = [{"role": "user", "content": prompt}]
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0
        )
        return response.choices[0].message.content
    
    #no stored memory for this chatbot
    def just_chatbot(self,user_input):
        prompt = f"""
        You are a my interviewer and its my {self.topic} interview. 
        Ask me theoretical questions and my replies will be the answers I type out. 
        Tell me how I do and keep asking unique and different questions . 
        Try to cover all the possible questions.
        Don't deep dive into a single question unless I explicitly ask for it.
        User input: {user_input}"""
        output = self.conversation.predict(input=prompt)
        return output

    #this chatbot stores memory
    def memory_chatbot(self, user_input):
        conversation = ConversationChain(llm=self.client,memory=self.memory)
        output = conversation.predict(input=user_input)
        self.memory.save_context({"input": user_input}, {"output": output})
        return output

    
        