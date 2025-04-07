from groq import Groq
from groq.types.chat.chat_completion import ChatCompletion
from typing import List, Dict
import os

class groqinference:
    def __init__(self, model: str = "llama-3.2-11b-vision-preview"):
        os.environ["groq_api_key"] = os.getenv("groq_api_key")
        self.groq_client = Groq()
        self.model = model
    
    def generate_responce(self, messages: List[Dict], temperature=1, max_completion_tokens=1024):
        """
        Generate a response using Groq's LLM.

        Args: 
            messages:List of message dictionaries with 'role' and 'content' keys

        Returns:
            str: The generated response from the model
        
        """
        try:
            completion = self.groq_client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_completion_tokens
            )
            return completion.choices[0].message.content
        except Exception as e:
            print("Error generating response:", e)  # Debugging line
            return "Error generating response."