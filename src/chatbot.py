import os
from langchain_openai import OpenAI

from langchain_core.chat_history import BaseChatMessageHistory
from src.database_models import ChatMessage
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_core.runnables.history import RunnableWithMessageHistory

class ChatBot:
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        self.topic = None
        self.chat = ChatOpenAI(api_key=api_key, model="gpt-3.5-turbo-0125")

    def set_topic(self, topic):
        self.topic = topic

    # Get all the messages for a particular user and topic
    def get_session_history(self,session_id) -> BaseChatMessageHistory:
        user,topic = session_id.split("_")
        user_id = int(user)
        
        chat_history = ChatMessageHistory()

        previous_messages = ChatMessage.query.filter_by(user_id=user_id, topic=topic).order_by(ChatMessage.timestamp).all()

        for msg in previous_messages:
            if msg.sender == 'user':
                chat_history.add_user_message(msg.message)
            elif msg.sender == 'bot':
                chat_history.add_ai_message(msg.message)

        return chat_history        
    # Method to summarize messages
    def summarize_messages(self, chat_history: ChatMessageHistory) -> bool:
        stored_messages = chat_history.messages
        if len(stored_messages) == 0:
            return False

        summarization_prompt = ChatPromptTemplate.from_messages(
            [
                ("placeholder", "{chat_history}"),
                (
                    "user",
                    "Distill the above chat messages into a single summary message. Include as many specific details as you can.",
                ),
            ]
        )
        summarization_chain = summarization_prompt | self.chat

        summary_message = summarization_chain.invoke({"chat_history": stored_messages})
        print("Summary",summary_message)

        chat_history.clear()
        chat_history.add_ai_message(summary_message)

        return True
    
    # Method to generate a response based on user input and session history
    def generate_response(self, input_message: str, session_id: str) -> str:
        chat_history = self.get_session_history(session_id)
        user,topic = session_id.split("_")

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    f"""You are an here to help me practice concepts for the topic of {topic}. 
                    Please only ask questions relevant to {topic} and avoid discussing any other topics. 
                    Your role is to ask insightful questions based on the chat history and provide feedback on my answers.""",
                ),
                ("placeholder", "{chat_history}"),
                ("user", "{input}"),
            ]
        )

        # Combine prompt and AI client for response generation
        chain = prompt | self.chat

        # Simulate message history and invoke the chat
        chain_with_message_history = RunnableWithMessageHistory(
            chain,
            lambda session_id: chat_history,
            input_messages_key="input",
            history_messages_key="chat_history",
        )

        self.summarize_messages(chat_history)

        response = chain_with_message_history.invoke(
            {"input": input_message},
            {"configurable": {"session_id": session_id}},
        )

        return response.content

    # Method to handle a full chatbot flow
    def run_chain(self, input_message: str, session_id: str):
        return self.generate_response(input_message, session_id)

